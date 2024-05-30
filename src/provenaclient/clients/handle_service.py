from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
from enum import Enum 
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *


class HandleAPIEndpoints(str, Enum):
    """An ENUM containing the handle api endpoints."""
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    POST_HANDLE_MINT = "/handle/mint"
    POST_HANDLE_ADD_VALUE = "/handle/add_value"
    POST_HANDLE_ADD_VALUE_BY_INDEX = "/handle/add_value_by_index"
    GET_HANDLE_GET = "/handle/get"
    GET_HANDLE_LIST = "/handle/list"
    PUT_HANDLE_MODIFY_BY_INDEX = "/handle/modify_by_index"
    POST_HANDLE_REMOVE_BY_INDEX = "/handle/remove_by_index"
    GET_HEALTH_CHECK = "/"

# L2 interface.
class HandleServiceClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the HandleServiceClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: HandleAPIEndpoints) -> str:
        return self._config.handle_service_api_endpoint + endpoint.value
