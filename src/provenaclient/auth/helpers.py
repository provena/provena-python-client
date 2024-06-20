'''
Created Date: Tuesday June 18th 2024 +1000
Author: peter
-----
Last Modified: Tuesday June 18th 2024 12:44:03 pm +1000
Modified By: peter
-----
Description: Miscellaneous helper functions assisting with implementation of auth flows
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime, timezone
from typing import Generator, Optional, Dict, List
from httpx import Auth, Request, Response
from jose import jwt, JWTError # type: ignore
from jose.constants import ALGORITHMS # type: ignore
import requests
import logging


# Default constant value for JWT Expiry Window in seconds.
JWT_DEFAULT_WINDOW = 30


class AccessToken(BaseModel):
    access_token: str


class Tokens(BaseModel):
    access_token: str
    # refresh tokens are marked as optional because offline tokens should not be cached
    refresh_token: Optional[str]


class HttpxBearerAuth(Auth):
    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers['Authorization'] = "Bearer " + self.token
        yield request


def check_token_expiry_window(jwt_data: dict[str, Any], logger: logging.Logger, jwt_token_expiry_window: int = JWT_DEFAULT_WINDOW) -> bool:
    """This helper function checks if the current JWT token will 
    expire or not expire either within the provided or default (30sec)  window.
    If the token is going to be expired in less than or within the provided or default (30sec).
    expiry window they will be refreshed. 

    Parameters
    ----------
    jwt_data : dict[str,Any]
        A dictionary containing the token validation results.
    jwt_token_expiry_window: Optional[int]
        A potential integer value containing your desired JWT expiry 
        window.

    Returns
    -------
    bool
        True: The current token will not expire within 30 seconds
        False: The current token will expire within 30 seconds.
    """

    # Contains an unix timestamp
    expiration_timestamp = jwt_data.get("exp")

    if expiration_timestamp:

        # We will need to convert to a datetime/utc object here.
        expiration_time = datetime.fromtimestamp(
            expiration_timestamp, timezone.utc)
        current_time = datetime.now(timezone.utc)
        remaining_time = (expiration_time - current_time).total_seconds()

        if remaining_time <= jwt_token_expiry_window:
            return False

        else:
            return True

    return False

def retrieve_keycloak_public_key(keycloak_endpoint: str, logger: logging.Logger) -> str:
        """Given the keycloak endpoint, retrieves the advertised
        public key.
        Based on https://github.com/nurgasemetey/fastapi-keycloak-oidc/blob/main/main.py
        """
        error_message = f"Error finding public key from keycloak endpoint {keycloak_endpoint}."
        try:
            r = requests.get(url=keycloak_endpoint,
                             timeout=3)
            r.raise_for_status()
            response_json = r.json()
            return f"-----BEGIN PUBLIC KEY-----\r\n{response_json['public_key']}\r\n-----END PUBLIC KEY-----"
        except requests.exceptions.HTTPError as errh:
            logger.info(error_message)
            logger.info("Http Error:" + str(errh))
            raise errh
        except requests.exceptions.ConnectionError as errc:
            logger.info(error_message)
            logger.info("Error Connecting:" + str(errc))
            raise errc
        except requests.exceptions.Timeout as errt:
            logger.info(error_message)
            logger.info("Timeout Error:" + str(errt))
            raise errt
        except requests.exceptions.RequestException as err:
            logger.info(error_message)
            logger.info("An unknown error occured: " + str(err))
            raise err

def keycloak_refresh_token_request(token_endpoint: str, client_id: str, scopes: List[str], refresh_token:str, logger: logging.Logger) -> Dict[str, Any]:
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

    # Perform a refresh grant
    refresh_grant_type = "refresh_token"

    # Required openid connect fields
    data = {
        "grant_type": refresh_grant_type,
        "client_id": client_id,
        "refresh_token": refresh_token,
        "scope": " ".join(scopes)
    }

    logger.info("Attempting to refresh token.")

    # Send API request
    response = requests.post(token_endpoint, data=data)

    if (not response.status_code == 200):
            err_msg = f"The token used for refresh is invalid or has potentially expired. Something went wrong during token refresh. Status code: {response.status_code}."
            logger.error(err_msg)
            raise Exception(err_msg)

    return response.json()


def validate_access_token(public_key: str, access_token: str, logger: logging.Logger) -> bool:
    """Uses the python-jose library to validate current creds.

    In this context, it is basically just checking signature
    and expiry. The tokens are enforced at the API side 
    as well.

    Parameters
    ----------
    tokens : Optional[Tokens], optional
        The tokens object to validate, by default None
    """

    logger.info("Attempting to validate tokens.")

    try:

        jwt_response = jwt.decode(
            access_token,
            public_key,
            algorithms=[ALGORITHMS.RS256],
            options={
                "verify_signature": True,
                "verify_aud": False,
                "exp": True
            }
        )

        token_is_fresh = check_token_expiry_window(jwt_data=jwt_response, logger=logger)

        if not token_is_fresh:
            logger.info(
                "Token is expiring soon and need to be refreshed.")
        else:
            logger.info("Token validation successful.")

        return token_is_fresh

    except JWTError as e:
        logger.info(f"Token Validation Error {e}")
        return False
