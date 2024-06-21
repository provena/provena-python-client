'''
Created Date: Tuesday June 18th 2024 +1000
Author: Peter Baker
-----
Last Modified: Tuesday June 18th 2024 12:44:03 pm +1000
Modified By: Peter Baker
-----
Description: Implementations of the Auth interface defined in auth/manager.py
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from typing import Any, Dict, Optional
from provenaclient.auth.manager import AuthManager, LogType
import requests
import webbrowser
import time
import os
from provenaclient.auth.helpers import AccessToken, Tokens, keycloak_refresh_token_request, validate_access_token, retrieve_keycloak_public_key
import json
from provenaclient.auth.manager import DEFAULT_LOG_LEVEL
from provenaclient.utils.config import Config


class DeviceFlow(AuthManager):
    keycloak_endpoint: str
    client_id: str
    scopes: list
    device_endpoint: str
    token_endpoint: str

    def __init__(self, config: Config, client_id: str, log_level: Optional[LogType] = None) -> None:
        f""" Create and generate a DeviceFlow object. The tokens are automatically refreshed when
        accessed through the get_auth() function.

        Tokens are cached in local storage with a configurable file name and are
        only reproduced if the refresh token expires.

        Parameters
        ----------
        keycloak_endpoint : str
            The keycloak endpoint to use.
        client_id : str
            The client id for the keycloak authorisation.
        log_level: Optional[LogType]
            The logging level to use - defaults to {DEFAULT_LOG_LEVEL} 
        """

        # construct parent class and include log level
        super().__init__(log_level=log_level)

        self.keycloak_endpoint = config.keycloak_endpoint
        self.client_id = client_id
        self.scopes: list = []
        self.file_name = ".tokens.json"
        self.device_endpoint = f'{self.keycloak_endpoint}/protocol/openid-connect/auth/device'
        self.token_endpoint = f'{self.keycloak_endpoint}/protocol/openid-connect/token'

        try:
            # First thing to do here is obtain the keycloak public key.
            self.public_key = retrieve_keycloak_public_key(
                logger=self.logger,
                keycloak_endpoint=self.keycloak_endpoint,
            )

        except Exception as e:
            raise Exception(
                "Failed to retrieve the Keycloak public key, authentication cannot proceed.") from e

        # Second thing will be to check if the tokens.json file is already present or not.
        # If it's present validate it, if fails then refresh else not present then fetch new tokens.
        if os.path.exists(self.file_name):
            self.tokens = self.load_tokens()
            if not self.tokens:
                self.logger.info(
                    "No tokens found or failed to load tokens.")
                self.start_device_flow()
            else:
                # Attempt to validate tokens
                if validate_access_token(
                    logger=self.logger,
                    access_token=self.tokens.access_token,
                    public_key=self.public_key
                ):
                    self.logger.info("Tokens are valid...")
                else:
                    try:
                        self.refresh_tokens()
                    except Exception as e:
                        self.logger.info(
                            f"Refresh token has expired or is invalid {e}")
                        self.start_device_flow()
        else:
            self.logger.info("No token file found, starting device flow.")
            self.start_device_flow()

    def get_token(self) -> str:
        """
        IMPLEMENTS BASE METHOD 

        Uses the current token - validates it,
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
            if validate_access_token(public_key=self.public_key, access_token=self.tokens.access_token, logger=self.logger):
                return self.tokens.access_token
            
            # didnt return, refresh and try again. 
            self.logger.info("Token was invalid. Attempting Refresh")
            self.refresh_tokens()
            if validate_access_token(public_key=self.public_key, access_token=self.tokens.access_token, logger=self.logger):
                return self.tokens.access_token
            
            # still no good, restart flow
            self.logger.info("Token was invalid after refresh. Re-iniating Device Flow")
            self.start_device_flow()
            if validate_access_token(public_key=self.public_key, access_token=self.tokens.access_token, logger=self.logger):
                return self.tokens.access_token

        except Exception as e:
            self.logger.info("Something went wrong during get_token operation. Starting device flow.")
            self.start_device_flow()
            if validate_access_token(public_key=self.public_key, access_token=self.tokens.access_token, logger=self.logger):
                return self.tokens.access_token
        
        # no error, but also no valid token. Something is wrong.
        err_msg = "Failed to obtain a valid token after refreshing and initiating a new device flow."
        self.logger.error(err_msg)
        raise Exception(err_msg)
            

    def force_refresh(self) -> None:
        """
        IMPLEMENTS BASE METHOD 
        A method to reset the current authentication state.
        """

        # Force refresh everything hear, so reset the tokens file and re-generate the device flow.
        self.clear_token_storage()
        self.start_device_flow()

    def refresh_tokens(self) -> None:
        """Attempts to refresh the authentication tokens using a stored refresh token. This method
        updates the current tokens if the refresh is successful.

        Raises
        ------
        ValueError
            If no initial tokens are set, indicating that there is nothing to refresh. 
        ValueError
            If the refresh operation fails due to missing access or refresh tokens in the response,
            suggesting a failure in the refresh process.
        """

        if self.tokens is None:
            raise ValueError(
                "Token refresh attempted with no initial tokens set. ")

        self.logger.info("Refreshing using refresh token")

        refreshed: Dict[str, Any] = self.make_token_refresh_request()

        access_token = refreshed.get('access_token')
        refresh_token = refreshed.get('refresh_token')

        if not access_token or not refresh_token:
            error_message = "Failed to refresh tokens: Missing access or refresh tokens"
            self.logger.info(error_message)
            raise ValueError(error_message)
        else:
            self.tokens = Tokens(
                access_token=access_token,
                refresh_token=refresh_token
            )
            self.save_tokens(self.tokens)

    def save_tokens(self, tokens: Tokens) -> None:
        """Saves authentication tokens to a local file in JSON format.

        Parameters
        ----------
        tokens : Tokens
            An object representing the authentication tokens containing 
            the access and refresh tokens.

        Raises
        -------
        Generic Exception
            A generic exception is raised that handles errors from IO/File operations.

        """
        self.logger.info("Saving tokens into local storage.")

        try:

            with open(self.file_name, 'w') as file:
                json.dump(tokens.dict(), file)
                self.logger.info("Tokens saved to file successfully.")

        except Exception as e:
            print(f"Failed to save tokens: {e}")

    def clear_token_storage(self) -> None:
        """Checks if the tokens.json file exists and accordingly removes it and resets
        token object saved to class variable.
        """
        if os.path.exists("tokens.json"):
            os.remove("tokens.json")
            self.logger.info("Stored tokens have been clear.")

        self.tokens = None

    def load_tokens(self) -> Optional[Tokens]:
        """Loads authentication tokens from a local JSON file and returns them as a Tokens object.

        Returns
        -------
        Tokens
            An object representing the authentication tokens containing 
            the access and refresh tokens.

        Raises
        -------
        Generic Exception
            A generic exception is raised that handles errors from IO/File operations.

        """

        self.logger.info("Looking for existing tokens in local storage.")

        try:
            with open(self.file_name, 'r') as file:
                token_data = json.load(file)
                return Tokens(**token_data)
        except Exception as e:
            print(f"Failed to load tokens: {e}")
            return None

    def make_token_refresh_request(self, tokens: Optional[Tokens] = None) -> Dict[str, Any]:
        """Performs the token refresh by making an HTTP post request to the token endpoint
        to obtain new access and refresh tokens.

        Parameters
        ----------
        tokens : Optional[Tokens], optional
            An optional Tokens object containing the refresh token. If not provided,
            the method will use the class variable stored tokens. 

            By default this parameter is None.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the new access and refresh tokens if the refresh is successful.

        Raises
        ------
        ValueError
            If no refresh token is provided or found in the class token variable. 
        Exception
            If the HTTP request fails a message is displayed with the HTTP status code. Can occur 
            if the refresh token has expired.
        """

        # make sure we have tokens to use
        desired_tokens: Optional[Tokens]
        if tokens:
            desired_tokens = tokens
        else:
            desired_tokens = self.tokens

        if not desired_tokens or not desired_tokens.refresh_token:
            raise ValueError("Refresh token is required but was not provided.")

        return keycloak_refresh_token_request(
            logger=self.logger,
            client_id=self.client_id,
            refresh_token=desired_tokens.refresh_token,
            scopes=self.scopes,
            token_endpoint=self.token_endpoint
        )

    def start_device_flow(self) -> None:
        """Initiates the device authorisation flow by requesting a device code from server and prompts
        user for authentication through the web browser and continues to handle the flow.

        Raises
        ------
        Exception
            If the request to the server fails or if the server response is not of status code 200,
            suggesting that the flow could not initiated.
        """

        self.logger.info("Initiating auth device flow.")

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
                self.logger.info("No data received in the response.")

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
                    self.logger.info("Missing or invalid access token.")
                    continue  # Skip this iteration, as we were not able to obtain a successful token

                if not refresh_token:
                    misc_fail = True
                    self.logger.info("Missing or invalid refresh token.")
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
                self.logger.info(f"Failed due to {response_data['error']}")

            else:
                self.logger.info(
                    f"Failed with unknown error, failed to find error message.")


class OfflineFlow(AuthManager):
    # The keycloak endpoint to target for tokens
    keycloak_endpoint: str
    # The offline token provided by user
    offline_token: str
    # The client ID to target for auth
    client_id: str
    # The token endpoint to use
    token_endpoint: str

    scopes: list

    public_key: str

    def __init__(self, config: Config, client_id: str, offline_token: Optional[str] = None, offline_token_file: Optional[str] = None, log_level: Optional[LogType] = None) -> None:
        f"""Create and generate an OfflineFlow object. Instatiate from provided offline token, or attempt to read
        one from file and generate the access token. Can provide the offline token directly, a file for it stored as plain text.

        Parameters
        ----------
        keycloak_endpoint : str
            The keycloak endpoint to use. E.g., https://auth.example.org/auth/realms/my_realm",
        client_id : str
            The client to target for auth. E.g., landing-portal-ui
        offline_token : Optional[str], optional
            The offline token to use for generating access tokens from. If not provided, defaults to None and init will try use offline_token_file to read an offline_token.
        offline_token_file : Optional[str], optional
            The file name to read the offline token from, where it is stored as plain text. Be sure to add this file to your .gitignore if using this parameter.

        Raises
        ------
        Exception
            Fails to retrive public key from keycloak endpoint.
        Exception
            Fails to validate new tokens generated from using the supplied offline token (Only if offline token is provided)
        Exception
            Fails to validate refreshed tokens from using the offline token in the default file (Only if loading from file)
        """
        # construct parent class and include log level
        super().__init__(log_level=log_level)

        self.keycloak_endpoint = config.keycloak_endpoint
        self.client_id = client_id
        self.scopes: list = []

        self.token_endpoint = f'{self.keycloak_endpoint}/protocol/openid-connect/token'

        try:
            # First thing to do here is obtain the keycloak public key.
            self.public_key = retrieve_keycloak_public_key(
                logger=self.logger,
                keycloak_endpoint=self.keycloak_endpoint,
            )
        except Exception as e:
            raise Exception(
                "Failed to retrieve the Keycloak public key, authentication cannot proceed.") from e

        if not offline_token and not offline_token_file:
            err_msg = "Please provide a value or offline_token or offline_token_file."
            self.logger.error(err_msg)
            raise ValueError(err_msg)

        if offline_token:
            self.logger.info(
                "Offline token provided, attempting to generate tokens from it.")
            self.offline_token = offline_token
        elif offline_token_file:
            self.logger.info(
                "Offline token file provided, attempting to generate tokens from it.")
            self.offline_token = self.load_offline_token(offline_token_file)
        else:
            err_msg = "Please provide a value or offline_token or offline_token_file."
            self.logger.error(err_msg)
            raise ValueError(err_msg)

        # Ok, got an offline token, now generate an temporary access token from it
        try:
            self.get_access_token_from_offline_token()
        except Exception as e:
            err_msg = "Failed to validate new tokens generated from offline token file."
            self.logger.error(err_msg)
            raise Exception(err_msg) from e

    def get_token(self) -> str:
        """
        IMPLEMENTS BASE METHOD

        Uses the current token - validates it, 
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
            if validate_access_token(
                    logger=self.logger,
                access_token=self.tokens.access_token,
                public_key=self.public_key
            ):
                return self.tokens.access_token
            else:
                self.logger.info("Token was invalid. Attempting Refresh")
                # refresh with refresh token and attempt re validation
                self.get_access_token_from_offline_token()
                if validate_access_token(
                    logger=self.logger,
                    access_token=self.tokens.access_token,
                    public_key=self.public_key
                ):
                    return self.tokens.access_token
                # still here, error
                err_msg = "Failed to produce a valid access token from the offline token."
                self.logger.error(err_msg)
                raise Exception(
                    err_msg)
        except Exception as e:
            err_msg = "Failed to refresh token."
            self.logger.error(err_msg)
            raise Exception(err_msg) from e

    def force_refresh(self) -> None:
        """
        IMPLEMENTS BASE METHOD 

        A method to reset the current authentication state.

        Since the offline flow has no cached state - this just forces a refresh
        token request to be made.
        """

        self.get_access_token_from_offline_token()

    def get_access_token_from_offline_token(self) -> None:
        tokens = keycloak_refresh_token_request(
            logger=self.logger,
            client_id=self.client_id,
            token_endpoint=self.token_endpoint,
            scopes=self.scopes,
            refresh_token=self.offline_token
        )

        access_token = tokens.get('access_token')
        if not access_token:
            err_msg = "Failed to geneate access token. Returned access token is None."
            self.logger.error(err_msg)
            raise ValueError(err_msg)

        self.tokens = AccessToken(
            access_token=access_token
        )

    def load_offline_token(self, file_name: str) -> str:
        """Loads the offline token from the provided file.

        Parameters
        ----------
        file_name : str
            The file name to load the offline token from.

        Returns
        -------
        str
            The offline token read from the file.

        Raises
        ------
        Exception
            If the file does not exist or if the file is empty.
        """

        if not os.path.exists(file_name):
            err_msg = f"Offline token file named {file_name} does not exist."
            self.logger.error(err_msg)
            raise Exception(err_msg)

        with open(file_name, 'r') as f:
            offline_token = f.read().strip()

        if not offline_token or offline_token == "":
            err_msg = f"File {file_name} is empty."
            self.logger.error(err_msg)
            raise Exception(err_msg)

        return offline_token
