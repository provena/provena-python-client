from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from ProvenaInterfaces.AuthAPI import *
from provenaclient.clients.client_helpers import *
from enum import Enum
from provenaclient.utils.helpers import *

class AuthEndpoints(str, Enum):
    # Contains all AuthAPI endpoints - to regen use
    # generate_open_api_endpoint_dump.py with openapi.json as auth-api open api
    # spec (from /openapi.json)
    GET_CHECK_ACCESS_PUBLIC = "/check-access/public"
    GET_CHECK_ACCESS_GENERAL = "/check-access/general"
    GET_ACCESS_CONTROL_ADMIN_ALL_PENDING_REQUEST_HISTORY = "/access-control/admin/all-pending-request-history"
    GET_ACCESS_CONTROL_ADMIN_ALL_REQUEST_HISTORY = "/access-control/admin/all-request-history"
    GET_ACCESS_CONTROL_ADMIN_USER_PENDING_REQUEST_HISTORY = "/access-control/admin/user-pending-request-history"
    GET_ACCESS_CONTROL_ADMIN_USER_REQUEST_HISTORY = "/access-control/admin/user-request-history"
    POST_ACCESS_CONTROL_ADMIN_ADD_NOTE = "/access-control/admin/add-note"
    POST_ACCESS_CONTROL_ADMIN_CHANGE_REQUEST_STATE = "/access-control/admin/change-request-state"
    POST_ACCESS_CONTROL_ADMIN_DELETE_REQUEST = "/access-control/admin/delete-request"
    POST_ACCESS_CONTROL_USER_REQUEST_CHANGE = "/access-control/user/request-change"
    GET_ACCESS_CONTROL_USER_REQUEST_HISTORY = "/access-control/user/request-history"
    GET_ACCESS_CONTROL_USER_PENDING_REQUEST_HISTORY = "/access-control/user/pending-request-history"
    GET_ACCESS_CONTROL_USER_GENERATE_ACCESS_REPORT = "/access-control/user/generate-access-report"
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    GET_GROUPS_ADMIN_LIST_GROUPS = "/groups/admin/list_groups"
    GET_GROUPS_ADMIN_DESCRIBE_GROUP = "/groups/admin/describe_group"
    GET_GROUPS_ADMIN_LIST_MEMBERS = "/groups/admin/list_members"
    GET_GROUPS_ADMIN_LIST_USER_MEMBERSHIP = "/groups/admin/list_user_membership"
    GET_GROUPS_ADMIN_CHECK_MEMBERSHIP = "/groups/admin/check_membership"
    POST_GROUPS_ADMIN_ADD_MEMBER = "/groups/admin/add_member"
    DELETE_GROUPS_ADMIN_REMOVE_MEMBER = "/groups/admin/remove_member"
    DELETE_GROUPS_ADMIN_REMOVE_MEMBERS = "/groups/admin/remove_members"
    POST_GROUPS_ADMIN_ADD_GROUP = "/groups/admin/add_group"
    DELETE_GROUPS_ADMIN_REMOVE_GROUP = "/groups/admin/remove_group"
    PUT_GROUPS_ADMIN_UPDATE_GROUP = "/groups/admin/update_group"
    GET_GROUPS_USER_LIST_GROUPS = "/groups/user/list_groups"
    GET_GROUPS_USER_DESCRIBE_GROUP = "/groups/user/describe_group"
    GET_GROUPS_USER_LIST_USER_MEMBERSHIP = "/groups/user/list_user_membership"
    GET_GROUPS_USER_LIST_MEMBERS = "/groups/user/list_members"
    GET_GROUPS_USER_CHECK_MEMBERSHIP = "/groups/user/check_membership"
    GET_GROUPS_ADMIN_EXPORT = "/groups/admin/export"
    POST_GROUPS_ADMIN_IMPORT = "/groups/admin/import"
    POST_GROUPS_ADMIN_RESTORE_FROM_TABLE = "/groups/admin/restore_from_table"
    GET_LINK_USER_LOOKUP = "/link/user/lookup"
    POST_LINK_USER_ASSIGN = "/link/user/assign"
    POST_LINK_USER_VALIDATE = "/link/user/validate"
    GET_LINK_ADMIN_LOOKUP = "/link/admin/lookup"
    POST_LINK_ADMIN_ASSIGN = "/link/admin/assign"
    DELETE_LINK_ADMIN_CLEAR = "/link/admin/clear"
    GET_LINK_ADMIN_REVERSE_LOOKUP = "/link/admin/reverse_lookup"
    GET_HEALTH_CHECK = "/"

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

    def _build_endpoint(self, endpoint: AuthEndpoints) -> str:
        return self._config.auth_api_endpoint + endpoint.value

    async def get_all_pending_request_history(self) -> AccessRequestList:
        """
        
        Gets all requests with pending status

        Returns:
            AccessRequestList: The response object
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_ADMIN_ALL_PENDING_REQUEST_HISTORY),
            error_message="Failed to retrieve admin pending request history...",
            params={},
            model=AccessRequestList
        )

    async def get_all_request_history(self) -> AccessRequestList:
        """
        
        Gets all requests

        Returns:
            AccessRequestList: The response object
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_ADMIN_ALL_REQUEST_HISTORY),
            error_message="Failed to retrieve admin request history...",
            params={},
            model=AccessRequestList
        )

    async def get_user_pending_request_history(self, username: str) -> AccessRequestList:
        """
        
        Gets pending requests for specified user

        Args:
            username (str): Username to query

        Returns:
            AccessRequestList: The response list
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_ADMIN_USER_PENDING_REQUEST_HISTORY),
            error_message="Failed to retrieve user pending request history...",
            params={"username": username},
            model=AccessRequestList
        )

    async def get_user_request_history(self, username: str) -> AccessRequestList:
        """
        
        Gets all requests for specified user

        Args:
            username (str): Username to query

        Returns:
            AccessRequestList: The response list
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_ADMIN_USER_REQUEST_HISTORY),
            error_message="Failed to retrieve user request history...",
            params={"username": username},
            model=AccessRequestList
        )

    async def post_add_note(self, note: RequestAddNote) -> None:
        """
        Adds a note to an existing request

        Args:
            note (RequestAddNote): Payload incl note info
        """
        await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_ACCESS_CONTROL_ADMIN_ADD_NOTE),
            error_message="Failed to add note.",
            params={},
            json_body=py_to_dict(note),
            model=StatusResponse
        )

    async def post_change_request_state(self, send_email_alert: bool, change: AccessRequestStatusChange) -> ChangeStateStatus:
        """
        
        Change state of a request. 

        Args:
            send_email_alert (bool): Should trigger email alert?
            change (AccessRequestStatusChange): The details of change

        Returns:
            ChangeStateStatus: The response object
        """
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.POST_ACCESS_CONTROL_ADMIN_CHANGE_REQUEST_STATE),
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
        return self._config.auth_api_endpoint + endpoint.value
