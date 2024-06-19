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

    def refresh_tokens(self) -> None:
        """Simulate refreshing tokens."""
        self.token = "refreshed_mock_access_token"
        self.refresh_token = "refreshed_mock_refresh_token"

    def force_refresh(self) -> None:
        """Simulate force refreshing tokens."""
        self.refresh_tokens()

    def get_token(self) -> str:
        """Return the mock access token."""
        return self.token

    def get_auth(self) -> HttpxBearerAuth:
        """Return a mock HttpxBearerAuth object."""
        return HttpxBearerAuth(token=self.token)

    def validate_token(self, tokens: Tokens) -> bool:
        """Simulate token validation."""
        return True


class MockedClientService(ClientService):

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self._auth = auth
        self._config = config


class MockRequestModel(BaseModel):
    foo: str

class MockResponseModel(BaseModel):
    bar: str