from httpx._models import Response
from pydantic import BaseModel
import requests
from typing import Generator, Optional
from httpx import Auth, Request

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["authorization"] = "Bearer " + self.token
        return r

class HttpxBearerAuth(Auth):
    def __init__(self, token: str) -> None:
        self.token = token
    
    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers['Authorization'] = "Bearer " + self.token
        yield request

class Tokens(BaseModel):
    access_token: str
    # refresh tokens are marked as optional because offline tokens should not be cached
    refresh_token: Optional[str]