from abc import ABC, abstractmethod
from provenaclient.auth.helpers import HttpxBearerAuth, Tokens
from typing import Optional, Dict, Any
import requests
import os
import json
from jose import jwt, JWTError
from jose.constants import ALGORITHMS  # type: ignore
from provenaclient.auth.helpers import check_token_expiry_window


class AuthManager(ABC):

    @abstractmethod
    def force_refresh(self) -> None:
        """ Force refresh the current token"""
        pass

    @abstractmethod
    def get_token(self) -> str:
        """Get token information and other metadata."""
        pass

    @abstractmethod
    def get_auth(self) -> HttpxBearerAuth:
        """Prepares and returns an auth object of Bearer type."""
        pass

    ############################################################
    #                       Helper methods
    ############################################################

    file_name: str = ".tokens.json"

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
            r = requests.get(url=self.keycloak_endpoint,
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

    def clear_token_storage(self) -> None:
        """Checks if the tokens.json file exists and accordingly removes it and resets
        token object saved to class variable.
        """
        if os.path.exists("tokens.json"):
            os.remove("tokens.json")
            self.optional_print("Stored tokens have been clear.")

        self.tokens = None

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
            if the refresh/offline token has expired.
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
        response = requests.post(self.token_endpoint, data=data)

        if (not response.status_code == 200):
            raise Exception(
                f"The refresh/offline token has potentially expired. Something went wrong during token refresh. Status code: {response.status_code}.")

        return response.json()

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

            token_is_fresh = check_token_expiry_window(jwt_data=jwt_response)

            if not token_is_fresh:
                self.optional_print(
                    "Token is expiring soon and need to be refreshed.")

            else:
                self.optional_print("Token validation successful.")

            return token_is_fresh

        except JWTError as e:
            self.optional_print(f"Token Validation Error {e}")
            return False

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
        return HttpxBearerAuth(token=token)
