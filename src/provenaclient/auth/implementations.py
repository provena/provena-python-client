from typing import Any, Dict, Optional
from provenaclient.auth.manager import AuthManager
import requests
import webbrowser
import time
import os
import json
from jose import JWTError  # type: ignore
from provenaclient.auth.helpers import HttpxBearerAuth, Tokens


class DeviceFlow(AuthManager):

    keycloak_endpoint: str
    client_id: str
    silent: bool
    scopes: list
    device_endpoint: str
    token_endpoint: str

    def __init__(self, keycloak_endpoint: str, client_id: str,  silent: bool = False) -> None:
        self.keycloak_endpoint = keycloak_endpoint
        self.client_id = client_id
        self.scopes: list = []
        self.device_endpoint = f'{keycloak_endpoint}/protocol/openid-connect/auth/device'
        self.token_endpoint = f'{keycloak_endpoint}/protocol/openid-connect/token'
        self.silent = silent

        """ Create and generate a DeviceFlow object. The tokens are automatically refreshed when
        accessed through the get_auth() function. 

        Tokens are cached in local storage with a configurable file name and are
        only reproduced if the refresh token expires.

        Parameters
        ----------
        keycloak_endpoint : str
            The keycloak endpoint to use.
        client_id : str
            The client id for the keycloak authorisation.
        silent : bool
            Force silence in the stdout outputs for use in context where
            printing would be irritating. By default False (helpful messages are
            printed).

        """

        try:
            # First thing to do here is obtain the keycloak public key.
            self.retrieve_keycloak_public_key()

        except Exception as e:
            raise Exception(
                "Failed to retrieve the Keycloak public key, authentication cannot proceed.") from e

        # Second thing will be to check if the tokens.json file is already present or not.

        # If it's present validate it, if fails then refresh else not present then fetch new tokens.

        if os.path.exists(self.file_name):
            self.tokens = self.load_tokens()

            if not self.tokens:
                self.optional_print(
                    "No tokens found or failed to load tokens.")
                self.start_device_flow()

            else:
                # Attempt to validate tokens
                if self.validate_token(self.tokens):
                    self.optional_print("Tokens are valid...")

                else:
                    try:
                        self.refresh_tokens()

                    except Exception as e:
                        self.optional_print(
                            f"Refresh token has expired or is invalid {e}")
                        self.start_device_flow()
        else:
            self.optional_print("No token file found, starting device flow.")
            self.start_device_flow()

    def start_device_flow(self) -> None:
        """Initiates the device authorisation flow by requesting a device code from server and prompts
        user for authentication through the web browser and continues to handle the flow. 

        Raises
        ------
        Exception
            If the request to the server fails or if the server response is not of status code 200,
            suggesting that the flow could not initiated.
        """

        self.optional_print("Initiating auth device flow.")

        data = {
            "client_id": self.client_id,
            "scopes": ' '.join(self.scopes)
        }

        response = requests.post(self.device_endpoint, data=data)

        if response.status_code == 200:
            response_data = response.json()
            self.device_code = response_data.get('device_code')
            self.interval = response_data.get('interval')
            verification_url = response_data.get('verification_uri_complete')
            user_code = response_data.get('user_code')
            self.display_device_auth_flow(
                user_code=user_code, verification_url=verification_url)
            self.handle_auth_flow()

        else:
            raise Exception("Failed to initiate device flow auth.")

    def display_device_auth_flow(self, user_code: str, verification_url: str) -> None:
        """Displays the current device auth flow challenge - first by trying to 
        open a browser window - if this fails then prints suggestion to stdout 
        to try using the URL manually.

        Parameters
        ----------
        user_code : str
            The user code
        verification_url : str
            The url which embeds challenge code
        """
        print(f"Verification URL: {verification_url}")
        print(f"User Code: {user_code}")
        try:
            webbrowser.open(verification_url)
        except Exception:
            print("Tried to open web-browser but failed. Please visit URL above.")

    def handle_auth_flow(self) -> None:
        """Handles the device authorisation flow by constantly polling the token endpoint until a token
        is received, an error is received or a timeout occurs. 
        """

        device_grant_type = "urn:ietf:params:oauth:grant-type:device_code"

        data = {
            "grant_type": device_grant_type,
            "device_code": self.device_code,
            "client_id": self.client_id,
            "scope": " ".join(self.scopes)
        }

        # Setup success criteria
        succeeded = False
        timed_out = False
        misc_fail = False

        # start time
        response_data: Optional[Dict[str, Any]] = None

        # Poll for success
        while not succeeded and not timed_out and not misc_fail:
            response = requests.post(self.token_endpoint, data=data)
            response_data = response.json()

            if response_data is None:
                misc_fail = True
                self.optional_print("No data received in the response.")

            elif response_data.get('error'):
                error = response_data['error']
                if error != 'authorization_pending':
                    misc_fail = True
                # Wait appropriate OAuth poll interval
                time.sleep(self.interval)
            else:

                # Successful as there was no error at the endpoint
                # We will produce a token object here.

                access_token = response_data.get("access_token")
                refresh_token = response_data.get("refresh_token")

                if not access_token:
                    misc_fail = True
                    self.optional_print("Missing or invalid access token.")
                    continue  # Skip this iteration, as we were not able to obtain a successful token

                if not refresh_token:
                    misc_fail = True
                    self.optional_print("Missing or invalid refresh token.")
                    continue  # Skip this iteration, as we were not able to obtain a successful token

                self.tokens = Tokens(
                    access_token=access_token,
                    refresh_token=refresh_token
                )

                # Save the tokens into '.token.json'
                self.save_tokens(self.tokens)
                succeeded = True

        if not succeeded:
            if response_data and "error" in response_data:
                self.optional_print(f"Failed due to {response_data['error']}")

            else:
                self.optional_print(
                    f"Failed with unknown error, failed to find error message.")

    def get_token(self) -> str:
        """Uses the current token - validates it, 
        refreshes if necessary, and returns the valid token
        ready to be used.

        Returns
        -------
        str
            The access token

        Raises
        ------
        Exception
            Raises exception if tokens/public_key are not setup - make sure 
            that the object is instantiated properly before calling this function.
        Exception
            If the token is invalid and cannot be refreshed.
        Exception
            If the token validation still fails after re-conducting the device flow.
        """

        if self.tokens is None or self.public_key is None:
            raise Exception(
                "Cannot generate token without access token or public key.")

        try:
            # Attempt to validate the current token.
            if self.validate_token(self.tokens):
                return self.tokens.access_token
        except JWTError as e:
            # This flow means that the tokens are invalid.
            # Now we will check if the refresh token is valid as well, and attempt to re-generate.

            try:
                self.refresh_tokens()
                if self.validate_token(self.tokens):
                    return self.tokens.access_token
                else:
                    raise Exception("Something has gone wrong..")

            except Exception as e:
                self.optional_print(
                    f"Refresh token has expired or is invalid {e}")
                # This mean something that the refresh token is invalid as well, and new set of tokens need to be re-generated.
                self.start_device_flow()

        if self.validate_token(self.tokens):
            return self.tokens.access_token

        else:
            raise Exception(
                "Failed to obtain a valid token after initiating a new device flow.")

    def force_refresh(self) -> None:
        """A method to reset the current authentication state. 
        """

        # Force refresh everything hear, so reset the tokens file and re-generate the device flow.
        self.clear_token_storage()
        self.start_device_flow()


class OfflineFlow(AuthManager):
    keycloak_endpoint: str
    offline_token: str
    client_id: str
    file_name: str

    token_endpoint: str
    silent: bool
    scopes: list
    public_key: str

    def __init__(self, keycloak_endpoint: str, client_id: str, offline_token: Optional[str] = None, silent: bool = False) -> None:
        f"""Create and generate an OfflineFlow object. Instatiate from provided offline token, or attempt to read
        one from file and generate the access token.

        Parameters
        ----------
        keycloak_endpoint : str
            The keycloak endpoint to use. E.g., https://auth.example.org/auth/realms/my_realm",
        client_id : str
            The client to target for auth. E.g., landing-portal-ui
        offline_token : Optional[str], optional
            The offline token to bootstrap the auth device from. If not provided, defaults to None and an offline token is read from file {self.file_name}
        silent : bool, optional
            Whether to print debug or not, by default False

        Raises
        ------
        Exception
            Fails to retrive public key from keycloak endpoint.
        Exception
            Fails to validate new tokens generated from using the supplied offline token (Only if offline token is provided)
        Exception
            Fails to validate refreshed tokens from using the offline token in the default file (Only if loading from file)
        """

        self.keycloak_endpoint = keycloak_endpoint
        self.client_id = client_id
        self.scopes: list = []

        self.token_endpoint = f'{keycloak_endpoint}/protocol/openid-connect/token'
        self.silent = silent
        self.offline_token = offline_token

        try:
            # First thing to do here is obtain the keycloak public key.
            self.retrieve_keycloak_public_key()
        except Exception as e:
            raise Exception(
                "Failed to retrieve the Keycloak public key, authentication cannot proceed.") from e

        # if an offline_token was provided, use it to generate the tokens, if not, try use the file to get the offline token
        if offline_token:
            self.optional_print(
                "Offline token provided, attempting to generate tokens from it.")
            self.offline_token = offline_token

            self.tokens = Tokens(
                access_token="To Be Refreshed",
                refresh_token=self.offline_token,
            )
            # refresh self.tokens()
            self.refresh_tokens()
            if self.validate_token(self.tokens):
                self.optional_print("Successfully refreshed tokens from file.")
                self.offline_token = self.tokens.refresh_token
            else:
                raise Exception("Failed to validate refreshed tokens.")

        else:  # no offline token provided, try read from file
            self.optional_print(
                "No offline token provided, attempting to load tokens from file.")
            assert os.path.exists(
                self.file_name), "No offline token provided and no tokens file found."
            self.tokens = self.load_tokens()

            if self.validate_token(self.tokens):
                self.optional_print(
                    "Successfully read already valid tokens from file.")
                self.offline_token = self.tokens.refresh_token
            else:  # invalid tokens were read from file, try refreshing them.
                self.refresh_tokens()
                if self.validate_token(self.tokens):
                    self.optional_print(
                        "Successfully refreshed tokens from file.")
                    self.offline_token = self.tokens.refresh_token
                else:
                    raise Exception(
                        "Failed to validate tokens refreshed from file.")

    def get_token(self) -> str:
        """Uses the current token - validates it, 
        refreshes if necessary, and returns the valid token
        ready to be used.

        Returns
        -------
        str
            The access token

        Raises
        ------
        Exception
            Raises exception if tokens/public_key are not setup - make sure 
            that the object is instantiated properly before calling this function.
        Exception
            If the token is invalid and cannot be refreshed.
        Exception
            If the token validation still fails after re-conducting the device flow.
        """

        if self.tokens is None or self.public_key is None:
            raise Exception(
                "Cannot generate token without access token or public key.")

        try:
            # Attempt to validate the current token.
            if self.validate_token(self.tokens):
                return self.tokens.access_token
            else:
                # refresh and attempt re validation
                self.refresh_tokens()
                if self.validate_token(self.tokens):
                    return self.tokens.access_token
                else:
                    raise Exception("Failed to validate token after refresh.")
        except JWTError as e:
            raise Exception("Failed to refresh tokens.") from e
        except Exception as e:
            raise Exception("Failed to refresh tokens.") from e

    def force_refresh(self) -> None:
        """A method to reset the current authentication state.

        Raises
        ------
        Exception
            If the token validation still fails after refresh.
        """
        self.clear_token_storage()
        self.tokens = Tokens(
            access_token="To Be Refreshed",
            refresh_token=self.offline_token,
        )

        self.refresh_tokens()
        if self.validate_token(self.tokens):
            self.optional_print("Successfully refreshed tokens.")
            self.offline_token = self.tokens.refresh_token
        else:
            raise Exception("Failed to validate tokens refreshed tokens.")
