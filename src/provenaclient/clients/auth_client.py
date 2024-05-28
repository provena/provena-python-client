from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from ProvenaInterfaces.AuthAPI import *
from provenaclient.clients.client_helpers import *
from enum import Enum
from provenaclient.utils.helpers import *


class AuthEndpoints(str, Enum):
    """An ENUM containing the auth api
    endpoints.
    """
    pass


class AdminAuthEndpoints(str, Enum):
    """An ENUM containing the auth api
    endpoints.
    """
    # Admin access control

    GET_ALL_PENDING_REQUEST_HISTORY = "/access-control/admin/all-pending-request-history"
    GET_ALL_REQUEST_HISTORY = "/access-control/admin/all-request-history"
    GET_USER_PENDING_REQUEST_HISTORY = "/access-control/admin/user-pending-request-history"
    GET_USER_REQUEST_HISTORY = "/access-control/admin/user-request-history"
    POST_ADD_NOTE = "/access-control/admin/add-note"
    POST_CHANGE_REQUEST_STATE = "/access-control/admin/change-request-state"
    POST_DELETE_REQUEST = "/access-control/admin/delete-request"


class AuthAdminSubClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the AuthClient admin sub client with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: AdminAuthEndpoints) -> str:
        return self._config.auth_api_endpoint + "/" + endpoint.value

    async def get_all_pending_request_history(self) -> AccessRequestList:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AdminAuthEndpoints.GET_ALL_PENDING_REQUEST_HISTORY),
            error_message="Failed to retrieve admin pending request history...",
            params={},
            model=AccessRequestList
        )

    async def get_all_request_history(self) -> AccessRequestList:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AdminAuthEndpoints.GET_ALL_REQUEST_HISTORY),
            error_message="Failed to retrieve admin request history...",
            params={},
            model=AccessRequestList
        )

    async def get_user_pending_request_history(self, username: str) -> AccessRequestList:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AdminAuthEndpoints.GET_USER_PENDING_REQUEST_HISTORY),
            error_message="Failed to retrieve user pending request history...",
            params={"username": username},
            model=AccessRequestList
        )

    async def get_user_request_history(self, username: str) -> AccessRequestList:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AdminAuthEndpoints.GET_USER_REQUEST_HISTORY),
            error_message="Failed to retrieve user request history...",
            params={"username": username},
            model=AccessRequestList
        )

    async def post_add_note(self, note: RequestAddNote) -> None:
        await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(AdminAuthEndpoints.POST_ADD_NOTE),
            error_message="Failed to add note.",
            params={},
            json_body=py_to_dict(note),
            model=StatusResponse
        )

    async def post_change_request_state(self, send_email_alert: bool, change: AccessRequestStatusChange) -> ChangeStateStatus:
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(
                AdminAuthEndpoints.POST_CHANGE_REQUEST_STATE),
            error_message="Failed to change request status.",
            params={
                "send_email_alert": send_email_alert
            },
            json_body=py_to_dict(change),
            model=ChangeStateStatus
        )

# L2 interface.


class AuthClient(ClientService):
    # Sub clients
    admin: AuthAdminSubClient

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the AuthClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

        self.admin = AuthAdminSubClient(auth=auth, config=config)

    def _build_endpoint(self, endpoint: AuthEndpoints) -> str:
        return self._config.auth_api_endpoint + "/" + endpoint.value
