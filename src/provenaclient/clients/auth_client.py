from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from ProvenaInterfaces.AuthAPI import *
from provenaclient.clients.client_helpers import *
from provenaclient.models import HealthCheckResponse
from enum import Enum
from provenaclient.utils.helpers import *


class AuthEndpoints(str, Enum):
    # Contains all AuthAPI endpoints - to regen use
    # generate_open_api_endpoint_dump.py with openapi.json as auth-api open api
    # spec (from /openapi.json)

    # NOT IMPLEMENTED
    GET_CHECK_ACCESS_PUBLIC = "/check-access/public"
    GET_CHECK_ACCESS_GENERAL = "/check-access/general"
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"

    # DONE
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
    GET_GROUPS_ADMIN_LIST_GROUPS = "/groups/admin/list_groups"
    GET_GROUPS_ADMIN_DESCRIBE_GROUP = "/groups/admin/describe_group"
    GET_GROUPS_ADMIN_LIST_MEMBERS = "/groups/admin/list_members"
    GET_GROUPS_ADMIN_LIST_USER_MEMBERSHIP = "/groups/admin/list_user_membership"
    GET_GROUPS_ADMIN_CHECK_MEMBERSHIP = "/groups/admin/check_membership"
    POST_GROUPS_ADMIN_ADD_MEMBER = "/groups/admin/add_member"
    DELETE_GROUPS_ADMIN_REMOVE_MEMBER = "/groups/admin/remove_member"
    POST_GROUPS_ADMIN_ADD_GROUP = "/groups/admin/add_group"
    DELETE_GROUPS_ADMIN_REMOVE_GROUP = "/groups/admin/remove_group"
    PUT_GROUPS_ADMIN_UPDATE_GROUP = "/groups/admin/update_group"
    GET_GROUPS_ADMIN_EXPORT = "/groups/admin/export"
    POST_GROUPS_ADMIN_IMPORT = "/groups/admin/import"
    POST_GROUPS_ADMIN_RESTORE_FROM_TABLE = "/groups/admin/restore_from_table"
    GET_GROUPS_USER_LIST_GROUPS = "/groups/user/list_groups"
    GET_GROUPS_USER_DESCRIBE_GROUP = "/groups/user/describe_group"
    GET_GROUPS_USER_LIST_USER_MEMBERSHIP = "/groups/user/list_user_membership"
    GET_GROUPS_USER_LIST_MEMBERS = "/groups/user/list_members"
    GET_GROUPS_USER_CHECK_MEMBERSHIP = "/groups/user/check_membership"
    GET_LINK_USER_LOOKUP = "/link/user/lookup"
    POST_LINK_USER_ASSIGN = "/link/user/assign"
    POST_LINK_USER_VALIDATE = "/link/user/validate"
    GET_LINK_ADMIN_LOOKUP = "/link/admin/lookup"
    POST_LINK_ADMIN_ASSIGN = "/link/admin/assign"
    DELETE_LINK_ADMIN_CLEAR = "/link/admin/clear"
    GET_LINK_ADMIN_REVERSE_LOOKUP = "/link/admin/reverse_lookup"

    # TODO
    GET_HEALTH_CHECK = "/"

    # TODO ISSUE
    # Cannot have post body in delete - need to change implementation
    DELETE_GROUPS_ADMIN_REMOVE_MEMBERS = "/groups/admin/remove_members"


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
            url=self._build_endpoint(
                AuthEndpoints.POST_ACCESS_CONTROL_ADMIN_ADD_NOTE),
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

    async def get_list_groups(self) -> ListGroupsResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_LIST_GROUPS),
            error_message="Failed to list admin groups.",
            params={},
            model=ListGroupsResponse
        )

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_DESCRIBE_GROUP),
            error_message="Failed to describe group.",
            params={'id': group_id},
            model=DescribeGroupResponse
        )

    async def get_list_members(self, group_id: str) -> ListMembersResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_LIST_MEMBERS),
            error_message="Failed to list group members.",
            params={'id': group_id},
            model=ListMembersResponse
        )

    async def get_list_group_membership(self, username: str) -> ListUserMembershipResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_LIST_MEMBERS),
            error_message="Failed to list user group membership.",
            params={'username': username},
            model=ListUserMembershipResponse
        )

    async def get_check_user_membership(self, username: str, group_id: str) -> CheckMembershipResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_CHECK_MEMBERSHIP),
            error_message="Failed to list user group membership.",
            params={'username': username, 'group_id': group_id},
            model=CheckMembershipResponse
        )

    async def post_groups_add_member(self, group_id: str, user: GroupUser) -> AddMemberResponse:
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.POST_GROUPS_ADMIN_ADD_MEMBER),
            error_message="Failed to add user to group",
            params={'group_id': group_id},
            json_body=py_to_dict(user),
            model=AddMemberResponse
        )

    async def delete_remove_member(self, group_id: str, username: str) -> RemoveMemberResponse:
        return await parsed_delete_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.DELETE_GROUPS_ADMIN_REMOVE_MEMBER),
            error_message="Failed to remove member from group.",
            params={'group_id': group_id, 'username': username},
            model=RemoveMemberResponse
        )

    async def post_add_group(self, group: UserGroupMetadata) -> AddGroupResponse:
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.POST_GROUPS_ADMIN_ADD_GROUP),
            error_message="Failed to add group.",
            json_body=py_to_dict(group),
            params={},
            model=AddGroupResponse
        )

    async def put_update_group(self, group: UserGroupMetadata) -> UpdateGroupResponse:
        return await parsed_put_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.PUT_GROUPS_ADMIN_UPDATE_GROUP),
            error_message="Failed to update gruop.",
            json_body=py_to_dict(group),
            params={},
            model=UpdateGroupResponse
        )

    async def get_export_groups(self) -> GroupsExportResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_GROUPS_ADMIN_EXPORT),
            error_message="Failed to export groups.",
            params={},
            model=GroupsExportResponse
        )

    async def post_import_groups(self, body: GroupsImportRequest) -> GroupsImportResponse:
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_GROUPS_ADMIN_IMPORT),
            error_message="Groups import failed.",
            json_body=py_to_dict(body),
            params={},
            model=GroupsImportResponse
        )

    async def post_restore_groups_from_table(self, table_name: str, body: GroupsRestoreRequest) -> GroupsImportResponse:
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.POST_GROUPS_ADMIN_RESTORE_FROM_TABLE),
            error_message="Groups restore from table failed.",
            json_body=py_to_dict(body),
            params={'table_name': table_name},
            model=GroupsImportResponse
        )

    async def get_link_lookup_username(self, username: str) -> AdminLinkUserLookupResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_LINK_ADMIN_LOOKUP),
            error_message="Failed to lookup user in link service.",
            params={'username': username},
            model=AdminLinkUserLookupResponse
        )

    async def get_link_reverse_lookup_username(self, person_id: str) -> UserLinkReverseLookupResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_LINK_ADMIN_REVERSE_LOOKUP),
            error_message="Failed to lookup reverse in link service.",
            params={'person_id': person_id},
            model=UserLinkReverseLookupResponse
        )

    async def post_link_assign(self, body: AdminLinkUserAssignRequest) -> AdminLinkUserAssignResponse:
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_LINK_ADMIN_ASSIGN),
            error_message="Failed to assign user link.",
            params={},
            json_body=py_to_dict(body),
            model=AdminLinkUserAssignResponse
        )

    async def delete_clear_link(self, username: str) -> AdminLinkUserClearResponse:
        return await parsed_delete_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.DELETE_LINK_ADMIN_CLEAR),
            error_message="Failed to clear link from user.",
            params={'username': username},
            model=AdminLinkUserClearResponse
        )

    # TODO this is not currently possible because the DELETE method should not have JSON body according to HTTPX
    # async def post_remove_members(self, group_id: str, username: str) -> RemoveMemberResponse:
    #    return await parsed_delete_request_with_status(
    #        client=self,
    #        url=self._build_endpoint(AuthEndpoints.DELETE_GROUPS_ADMIN_REMOVE_MEMBERS),
    #        error_message="Failed to remove member from group.",
    #        params={'group_id': group_id, 'username': username},
    #        model=RemoveMemberResponse
    #    )

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

    async def get_health_check(self) -> HealthCheckResponse:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_HEALTH_CHECK),
            error_message="Health check failed!",
            params={},
            model=HealthCheckResponse
        )

    async def get_user_request_history(self) -> AccessRequestList:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_USER_REQUEST_HISTORY),
            error_message="Failed to retrieve access request history.",
            params={},
            model=AccessRequestList
        )

    async def post_user_request_change(self, body: AccessReport, send_email: bool) -> StatusResponse:
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.POST_ACCESS_CONTROL_USER_REQUEST_CHANGE),
            error_message="Failed to request access change.",
            params={"send_email": send_email},
            json_body=py_to_dict(body),
            model=StatusResponse
        )

    async def get_user_pending_request_history(self) -> AccessRequestList:
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_USER_PENDING_REQUEST_HISTORY),
            error_message="Failed to retrieve access pending request history.",
            params={},
            model=AccessRequestList
        )

    async def get_user_generate_access_report(self) -> AccessReportResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_USER_GENERATE_ACCESS_REPORT),
            error_message="Failed to generate access report.",
            params={},
            model=AccessReportResponse
        )

    async def get_list_groups(self) -> ListGroupsResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_LIST_GROUPS),
            error_message="Failed to list groups",
            params={},
            model=ListGroupsResponse
        )

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_DESCRIBE_GROUP),
            error_message="Failed to describe group",
            params={'id': group_id},
            model=DescribeGroupResponse
        )

    async def get_list_membership(self) -> ListUserMembershipResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_LIST_USER_MEMBERSHIP),
            error_message="Failed to list group membership.",
            params={},
            model=ListUserMembershipResponse
        )

    async def get_list_group_members(self, group_id: str) -> ListMembersResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_LIST_MEMBERS),
            error_message="Failed to list group members",
            params={'id': group_id},
            model=ListMembersResponse
        )

    async def get_check_membership(self, group_id: str) -> CheckMembershipResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_CHECK_MEMBERSHIP),
            error_message="Failed to check membership.",
            params={'id': group_id},
            model=CheckMembershipResponse
        )

    async def get_link_lookup_username(self, username: str) -> UserLinkUserLookupResponse:
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_LINK_USER_LOOKUP),
            error_message="Failed to lookup user in link service.",
            params={'username': username},
            model=UserLinkUserLookupResponse
        )

    async def post_link_assign(self, body: UserLinkUserAssignRequest) -> UserLinkUserAssignResponse:
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_LINK_USER_ASSIGN),
            error_message="Failed to assign user link.",
            params={},
            json_body=py_to_dict(body),
            model=UserLinkUserAssignResponse
        )

    async def post_link_validate(self, body: UserLinkUserAssignRequest) -> UserLinkUserValidateResponse:
        # Doesn't assert status as we want the status response to fall through
        # to user
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_LINK_USER_VALIDATE),
            error_message="Failed to validate user link.",
            params={},
            json_body=py_to_dict(body),
            model=UserLinkUserValidateResponse
        )
