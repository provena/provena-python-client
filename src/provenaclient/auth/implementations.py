from typing import Any, Dict, Optional
from provenaclient.auth.manager import AuthManager
import requests
import webbrowser
import time
import os
import json
from jose import jwt, JWTError  # type: ignore
from jose.constants import ALGORITHMS  # type: ignore
from provenaclient.auth.helpers import HttpxBearerAuth, Tokens, check_token_expiry_window


class DeviceFlow(AuthManager):

    keycloak_endpoint: str
    client_id: str
    silent: bool
    scopes: list
    file_name: str
    device_endpoint: str
    token_endpoint: str

    def __init__(self, keycloak_endpoint: str, client_id: str,  silent: bool = False) -> None:
        self.keycloak_endpoint = keycloak_endpoint
        self.client_id = client_id
        self.scopes: list = []
        self.file_name = ".tokens.json"
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
            raise Exception("Failed to retrieve the Keycloak public key, authentication cannot proceed.") from e

        # Second thing will be to check if the tokens.json file is already present or not. 

        # If it's present validate it, if fails then refresh else not present then fetch new tokens.

        if os.path.exists(self.file_name):
            self.tokens = self.load_tokens()

            if not self.tokens:
                self.optional_print("No tokens found or failed to load tokens.")
                self.start_device_flow()

            else: 
                # Attempt to validate tokens
                if self.validate_token(self.tokens):
                    self.optional_print("Tokens are valid...")
                                    
                else: 
                    try:
                        self.refresh_tokens()
                    
                    except Exception as e:
                        self.optional_print(f"Refresh token has expired or is invalid {e}")
                        self.start_device_flow()
        else: 
            self.optional_print("No token file found, starting device flow.")
            self.start_device_flow()

    def optional_print(self, message: Optional[str] = None) -> None: 
        """Prints only if the silent value is not 
        flagged.

        Parameters
        ----------
        message : Optional[str], optional
            The message to print
        """

        if not self.silent:
            if message:
                print(message)
            else:
                print()

    def retrieve_keycloak_public_key(self) -> None:
        """Given the keycloak endpoint, retrieves the advertised
        public key.
        Based on https://github.com/nurgasemetey/fastapi-keycloak-oidc/blob/main/main.py
        """
        error_message = f"Error finding public key from keycloak endpoint {self.keycloak_endpoint}."
        try:
            r = requests.get(url= self.keycloak_endpoint,
                             timeout=3)
            r.raise_for_status()
            response_json = r.json()
            self.public_key = f"-----BEGIN PUBLIC KEY-----\r\n{response_json['public_key']}\r\n-----END PUBLIC KEY-----"
        except requests.exceptions.HTTPError as errh:
            self.optional_print(error_message)
            self.optional_print("Http Error:" + str(errh))
            raise errh
        except requests.exceptions.ConnectionError as errc:
            self.optional_print(error_message)
            self.optional_print("Error Connecting:" + str(errc))
            raise errc
        except requests.exceptions.Timeout as errt:
            self.optional_print(error_message)
            self.optional_print("Timeout Error:" + str(errt))
            raise errt
        except requests.exceptions.RequestException as err:
            self.optional_print(error_message)
            self.optional_print("An unknown error occured: " + str(err))
            raise err
    

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

        self.optional_print("Looking for existing tokens in local storage.")

        try:
            with open(self.file_name, 'r') as file:
                token_data = json.load(file)
                return Tokens(**token_data)
        except Exception as e:
            print(f"Failed to load tokens: {e}")
            return None

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
        self.optional_print("Saving tokens into local storage.")

        try:

            with open(self.file_name, 'w') as file:
                json.dump(tokens.dict(), file)
                self.optional_print("Tokens saved to file successfully.")

        except Exception as e:
            print(f"Failed to save tokens: {e}")
    
    def validate_token(self, tokens: Tokens) -> bool:
        
        """Uses the python-jose library to validate current creds.

        In this context, it is basically just checking signature
        and expiry. The tokens are enforced at the API side 
        as well.

        Parameters
        ----------
        tokens : Optional[Tokens], optional
            The tokens object to validate, by default None
        """

        self.optional_print("Attempting to validate provided tokens.")

        try:
        
            jwt_response = jwt.decode(
                tokens.access_token, 
                self.public_key, 
                algorithms=[ALGORITHMS.RS256],
                options={
                "verify_signature": True,
                "verify_aud": False,
                "exp": True
                }
            )

            is_token_expiring = check_token_expiry_window(jwt_data=jwt_response)

            if not is_token_expiring:
                self.optional_print("Token is expiring soon and need to be refreshed.")
            
            else:
                self.optional_print("Token validation successful.")

            return is_token_expiring
    
        except JWTError as e: 
           self.optional_print(f"Token Validation Error {e}")
           return False  


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
    
        response = requests.post(self.device_endpoint, data = data)

        if response.status_code == 200: 
            response_data= response.json()
            self.device_code = response_data.get('device_code')
            self.interval = response_data.get('interval')
            verification_url = response_data.get('verification_uri_complete')
            user_code = response_data.get('user_code')
            self.display_device_auth_flow(user_code=user_code, verification_url=verification_url)
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
            response =  requests.post(self.token_endpoint, data=data)
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
                    continue # Skip this iteration, as we were not able to obtain a successful token

                if not refresh_token:
                    misc_fail = True
                    self.optional_print("Missing or invalid refresh token.")
                    continue # Skip this iteration, as we were not able to obtain a successful token

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
                self.optional_print(f"Failed with unknown error, failed to find error message.")

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
            raise ValueError("Token refresh attempted with no initial tokens set. ")

        self.optional_print("Refreshing using refresh token")
        self.optional_print()

        refreshed: Dict[str, Any] = self.make_token_refresh_request()

        access_token = refreshed.get('access_token')
        refresh_token = refreshed.get('refresh_token')

        if not access_token or not refresh_token:
            error_message = "Failed to refresh tokens: Missing access or refresh tokens"
            self.optional_print(error_message)
            raise ValueError(error_message)

        else:
            self.tokens = Tokens(
                access_token=access_token,
                refresh_token=refresh_token
            )

            self.save_tokens(self.tokens)
    
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
            If the HTTP request fails a message is displayed with the HTTP status code.
        """
    
        # Perform a refresh grant
        refresh_grant_type = "refresh_token"

        # make sure we have tokens to use
        desired_tokens: Optional[Tokens]
        if tokens:
            desired_tokens = tokens
        else:
            desired_tokens = self.tokens

        if not desired_tokens or not desired_tokens.refresh_token:
            raise ValueError("Refresh token is required but was not provided.")

        # Required openid connect fields
        data = {
            "grant_type": refresh_grant_type,
            "client_id": self.client_id,
            "refresh_token": desired_tokens.refresh_token,
            "scope": " ".join(self.scopes)
        }

        # Send API request
        response =  requests.post(self.token_endpoint, data=data)

        if (not response.status_code == 200):
            raise Exception(
                f"Something went wrong during token refresh. Status code: {response.status_code}.")

        return response.json()



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
            raise Exception("Cannot generate token without access token or public key.")
        
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
                # This mean something that the refresh token is invalid as well, and new set of tokens need to be re-generated. 
                self.start_device_flow()   

        if self.validate_token(self.tokens):
            return self.tokens.access_token

        else: 
            raise Exception("Failed to obtain a valid token after initiating a new device flow.")
      
    def get_auth(self) -> HttpxBearerAuth:
        """A helper function which produces a BearerAuth object for use
        in the httpx library. For example: 

        manager = DeviceFlow(...)
        auth = manager.get_auth 
        httpx.post(..., auth=auth)

        Returns
        -------
        BearerAuth
            The httpx auth object.

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

        token = self.get_token()
        return HttpxBearerAuth(token = token)

    def clear_token_storage(self) -> None:
        """Checks if the tokens.json file exists and accordingly removes it and resets
        token object saved to class variable.
        """
        if os.path.exists("tokens.json"):
            os.remove("tokens.json")
            self.optional_print("Stored tokens have been clear.")

        self.tokens = None


    def force_refresh(self) -> None:
        """A method to reset the current authentication state. 
        """

        # Force refresh everything hear, so reset the tokens file and re-generate the device flow. 
        self.clear_token_storage()
        self.start_device_flow()


class OfflineFlow(AuthManager):

    def refresh(self) -> None:
        pass
        
    def get_token(self) -> str:
        return ""

    def force_refresh(self) -> None:
        pass
        







