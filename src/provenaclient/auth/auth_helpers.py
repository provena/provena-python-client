from pydantic import BaseModel
import requests
from typing import Optional, Any
from datetime import datetime, timezone

#Default constant value for JWT Expiry Window in seconds.
JWT_DEFAULT_WINDOW = 30

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["authorization"] = "Bearer " + self.token
        return r

class Tokens(BaseModel):
    access_token: str
    # refresh tokens are marked as optional because offline tokens should not be cached
    refresh_token: Optional[str]    


def check_token_expiry_window(jwt_data: dict[str,Any], jwt_token_expiry_window: Optional[int] = None) -> bool:
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

    jwt_token_expiry_window = jwt_token_expiry_window if jwt_token_expiry_window else JWT_DEFAULT_WINDOW
    
    # Contains an unix timestamp
    expiration_timestamp = jwt_data.get("exp") 

    if expiration_timestamp: 

        # We will need to convert to a datetime/utc object here. 
        expiration_time = datetime.fromtimestamp(expiration_timestamp, timezone.utc)
        current_time = datetime.now(timezone.utc)
        remaining_time = (expiration_time - current_time).total_seconds()

        if remaining_time <= jwt_token_expiry_window: 
            return False
        
        else: 
            return True

    return False
