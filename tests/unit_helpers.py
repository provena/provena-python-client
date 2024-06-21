'''
Created Date: Wednesday June 19th 2024 +0000
Author: Parth Kulkarni
-----
Last Modified: Friday June 21st 2024 11:30:24 am +0000
Modified By: Parth Kulkarni
-----
Description: Contains helper classes and functions utilised by the unit test. 
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
21-06-2024 | Parth Kulkarni | Mocked classes, client, request and response payloads.
'''




from typing import Optional, Type
from provenaclient.auth.helpers import HttpxBearerAuth, Tokens
from provenaclient.auth.manager import AuthManager
from provenaclient.clients.client_helpers import ClientService
from provenaclient.utils.config import Config
from provenaclient.utils.helpers import BaseModelType
from pydantic import BaseModel

class MockedAuthService(AuthManager):

    def __init__(self) -> None:
        self.token = "mock_access_token"
        self.refresh_token = "mock_refresh_token"
        self.public_key = "mock_public_key"

    def force_refresh(self) -> None:
        """Simulate force refreshing tokens."""
        pass

    def get_token(self) -> str:
        """Return the mock access token."""
        return self.token

    def get_auth(self) -> HttpxBearerAuth:
        """Return a mock HttpxBearerAuth object."""
        return HttpxBearerAuth(token=self.token)

class MockedClientService(ClientService):

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self._auth = auth
        self._config = config


class MockRequestModel(BaseModel):
    foo: str

class MockResponseModel(BaseModel):
    bar: str

def is_exception_in_chain(exc: BaseException, exception_type: Type[BaseException]) -> bool:
    """Checks for the presence of a specified exception type in the exception chain.

    Parameters
    ----------
    exc : BaseException
        The starting exception in the chain.
    exception_type : Type[BaseException]
        The exception type to search for in the chain.
    Returns
    -------
    bool
        True if the exception type is found, False otherwise.
    """
        
    current_exception: Optional[BaseException] = exc
    while current_exception:
        if isinstance(current_exception, exception_type):
            return True
        try:
            current_exception = current_exception.__context__
        except Exception:
            return False
    return False