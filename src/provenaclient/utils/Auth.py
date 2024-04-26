# Take a look at migrating the mdis-client-tools into here and see whats possible.

from typing import Any, Dict, Optional
from .AuthManager import AuthManager
import requests
import webbrowser
import time
from pydantic import BaseModel
import os
import json
from jose import jwt, JWTError  # type: ignore
from jose.constants import ALGORITHMS  # type: ignore
''''

This file will contain the various authentication flows (Device, Offline, etc) in various classes. 

Currently working on developing the device flow.

In this implementation I have assumed that the user will not worry about where they want tokens placed, hence not providing them with the ability to change the location. 

Furthermore, they probably wont have stages as they will just be interacting with an instance of Provena that is on PROD. 

'''


class Tokens(BaseModel):
    access_token: str
    # refresh tokens are marked as optional because offline tokens should not be cached
    refresh_token: Optional[str]

class DeviceFlow(AuthManager):
    def __init__(self, keycloak_endpoint: str, client_id: str):
        self.keycloak_endpoint = keycloak_endpoint
        self.client_id = client_id
        self.scopes = []
        self.device_endpoint = f"{self.keycloak_endpoint}/protocol/openid-connect/auth/device"
        self.token_endpoint = f"{self.keycloak_endpoint}/protocol/openid-connect/token"

    def init(self):

        # First thing to do here is obtain the keycloak public key. 
        self.retrieve_keycloak_public_key()

        # Second thing will be to check if the tokens.json file is already present or not. 

        # If it's present validate it, if fails then refresh else not present then fetch new tokens.

        if os.path.exists('tokens.json'):
            self.tokens = self.load_tokens()

            if self.tokens and self.validate_token(self.tokens):
                print("Using cached tokens...")

            else:
                self.refresh()

        else: 
            print("Cached tokens are invalid, starting device flow")
            self.start_device_flow()

    def retrieve_keycloak_public_key(self) -> None:
        """Given the keycloak endpoint, retrieves the advertised
        public key.
        Based on https://github.com/nurgasemetey/fastapi-keycloak-oidc/blob/main/main.py
        """
        error_message = f"Error finding public key from keycloak endpoint {self.keycloak_endpoint}."
        try:
            r = requests.get(self.keycloak_endpoint,
                             timeout=3)
            r.raise_for_status()
            response_json = r.json()
            self.public_key = f"-----BEGIN PUBLIC KEY-----\r\n{response_json['public_key']}\r\n-----END PUBLIC KEY-----"
        except requests.exceptions.HTTPError as errh:
           # self.optional_print(error_message)
            #self.optional_print("Http Error:" + str(errh))
            raise errh
        except requests.exceptions.ConnectionError as errc:
            #self.optional_print(error_message)
            #self.optional_print("Error Connecting:" + str(errc))
            raise errc
        except requests.exceptions.Timeout as errt:
            #self.optional_print(error_message)
            #self.optional_print("Timeout Error:" + str(errt))
            raise errt
        except requests.exceptions.RequestException as err:
            #self.optional_print(error_message)
            #self.optional_print("An unknown error occured: " + str(err))
            raise err
    

    def load_tokens(self) -> Tokens:

        try:
            with open('tokens.json', 'r') as file:
                token_data = json.load(file)
                return Tokens(**token_data)
        except Exception as e:
            print(f"Failed to load tokens: {e}")
            return None

    def save_tokens(self, tokens: Tokens):

        print("Called")

        with open('tokens.json', 'w') as file:
            json.dump(tokens.model_dump(), file)
        print("Tokens saved to file successfully.")

    
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

        try:
        
            jwt.decode(
                tokens.access_token, 
                self.public_key, 
                algorithms=[ALGORITHMS.RS256],
                options={
                "verify_signature": True,
                "verify_aud": False,
                "exp": True
                }
            )

            print("Token is valid.")
            return True
    
        except JWTError as e: 
            print(f"Token Validation Error {e}")

    def start_device_flow(self) -> None: 

        data = {
            "client_id": self.client_id, 
            "scopes": ' '.join(self.scopes)
        }
    
        response = requests.post(self.device_endpoint, data = data)

        if response.status_code == 200: 
            print("success")
            response_data= response.json()
            self.device_code = response_data.get('device_code')
            self.interval = response_data.get('interval')
            verification_url = response_data.get('verification_uri_complete')
            user_code = response_data.get('user_code')
            webbrowser.open(verification_url)
            self.handle_auth_flow()
        
        else: 
            raise Exception("Failed to initiate device flow auth.")
    

    def handle_auth_flow(self) -> None:

        print("in handle auth flow")

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

        # get requests session for repeated queries
        session = requests.session()

        # Poll for success
        while not succeeded and not timed_out and not misc_fail:
            response = session.post(self.token_endpoint, data=data)
            response_data = response.json()
            assert response_data
            if response_data.get('error'):
                error = response_data['error']
                if error != 'authorization_pending':
                    misc_fail = True
                # Wait appropriate OAuth poll interval
                time.sleep(self.interval)
            else:
                
                # Successful as there was no error at the endpoint
                # We will produce a token object here. 

                self.tokens = Tokens(
                access_token=response_data.get('access_token'),
                refresh_token=response_data.get('refresh_token')
                )

                # Save the tokens into 'token.json'

                self.save_tokens(self.tokens)
                
        try:
            assert response_data
            self.optional_print(f"Failed due to {response_data['error']}")
            return None
        except Exception as e:
            self.optional_print(
                f"Failed with unknown error, failed to find error message. Error {e}")
            return None
        
    
    def refresh(self):
        print("In refresh method.")

    def get_token(self):
        pass

    def get_auth(self):
        pass


    def force_refresh(self):
        pass
        

class OfflineFlow(AuthManager):
    def __init__(self):
        pass

    def init(self):
        pass

    def refresh(self):
        pass
        
    def get_token(self):
        pass

    def force_refresh(self):
        pass
        







