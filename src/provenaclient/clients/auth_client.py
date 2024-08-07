'''
Created Date: Friday May 31st 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday May 31st 2024 9:50:26 am +1000
Modified By: Peter Baker
-----
Description: The Auth API L2 Client
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Some issues with admin remove members interfaces - blocked on this
'''

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
        """
        
        Gets a list of groups

        Returns:
            ListGroupsResponse: List of groups
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_LIST_GROUPS),
            error_message="Failed to list admin groups.",
            params={},
            model=ListGroupsResponse
        )

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        """
        
        Describes a group by ID

        Args:
            group_id (str): The group

        Returns:
            DescribeGroupResponse: Description
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_DESCRIBE_GROUP),
            error_message="Failed to describe group.",
            params={'id': group_id},
            model=DescribeGroupResponse
        )

    async def get_list_members(self, group_id: str) -> ListMembersResponse:
        """
        Lists members of group

        Args:
            group_id (str): The gruop

        Returns:
            ListMembersResponse: The list of members
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_LIST_MEMBERS),
            error_message="Failed to list group members.",
            params={'id': group_id},
            model=ListMembersResponse
        )

    async def get_list_group_membership(self, username: str) -> ListUserMembershipResponse:
        """
        
        Gets list of groups a user is in

        Args:
            username (str): The username

        Returns:
            ListUserMembershipResponse: The list of groups
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_LIST_MEMBERS),
            error_message="Failed to list user group membership.",
            params={'username': username},
            model=ListUserMembershipResponse
        )

    async def get_check_user_membership(self, username: str, group_id: str) -> CheckMembershipResponse:
        """
        
        Checks user membership within a group

        Args:
            username (str): The username to target
            group_id (str): The group to check

        Returns:
            CheckMembershipResponse: Response
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_ADMIN_CHECK_MEMBERSHIP),
            error_message="Failed to list user group membership.",
            params={'username': username, 'group_id': group_id},
            model=CheckMembershipResponse
        )

    async def post_groups_add_member(self, group_id: str, user: GroupUser) -> AddMemberResponse:
        """
        
        Adds a member to a group

        Args:
            group_id (str): Id of group
            user (GroupUser): The user to add

        Returns:
            AddMemberResponse: The response
        """
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
        """
        
        Removes member from group

        Args:
            group_id (str): The id of group
            username (str): The user to remove

        Returns:
            RemoveMemberResponse: The response
        """
        return await parsed_delete_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.DELETE_GROUPS_ADMIN_REMOVE_MEMBER),
            error_message="Failed to remove member from group.",
            params={'group_id': group_id, 'username': username},
            model=RemoveMemberResponse
        )

    async def post_add_group(self, group: UserGroupMetadata) -> AddGroupResponse:
        """
        
        Adds a group/creates group

        Args:
            group (UserGroupMetadata): The group details

        Returns:
            AddGroupResponse: The response
        """
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
        """
        Updates group details

        Args:
            group (UserGroupMetadata): The group metadata

        Returns:
            UpdateGroupResponse: The response
        """
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
        """
        Exports all group details in specified format.

        Returns:
            GroupsExportResponse: The data dump
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_GROUPS_ADMIN_EXPORT),
            error_message="Failed to export groups.",
            params={},
            model=GroupsExportResponse
        )

    async def post_import_groups(self, body: GroupsImportRequest) -> GroupsImportResponse:
        """
        
        Imports groups from data dump back in

        Args:
            body (GroupsImportRequest): The import request incl. dump

        Returns:
            GroupsImportResponse: The response
        """
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_GROUPS_ADMIN_IMPORT),
            error_message="Groups import failed.",
            json_body=py_to_dict(body),
            params={},
            model=GroupsImportResponse
        )

    async def post_restore_groups_from_table(self, table_name: str, body: GroupsRestoreRequest) -> GroupsImportResponse:
        """
        
        Restores groups by first dumping from valid group table. 
        Needs permissions to table.

        Args:
            table_name (str): The table name
            body (GroupsRestoreRequest): The request

        Returns:
            GroupsImportResponse: The response details
        """
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
        """
        Gets the linked person for user

        Args:
            username (str): User to lookup

        Returns:
            AdminLinkUserLookupResponse: Response
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_LINK_ADMIN_LOOKUP),
            error_message="Failed to lookup user in link service.",
            params={'username': username},
            model=AdminLinkUserLookupResponse
        )

    async def get_link_reverse_lookup_username(self, person_id: str) -> UserLinkReverseLookupResponse:
        """
        
        Looks up reverse by person ID

        Args:
            person_id (str): The person to lookup

        Returns:
            UserLinkReverseLookupResponse: The response
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_LINK_ADMIN_REVERSE_LOOKUP),
            error_message="Failed to lookup reverse in link service.",
            params={'person_id': person_id},
            model=UserLinkReverseLookupResponse
        )

    async def post_link_assign(self, body: AdminLinkUserAssignRequest) -> AdminLinkUserAssignResponse:
        """
        
        Assigns a person to a given user

        Args:
            body (AdminLinkUserAssignRequest): The request

        Returns:
            AdminLinkUserAssignResponse: The response
        """
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_LINK_ADMIN_ASSIGN),
            error_message="Failed to assign user link.",
            params={},
            json_body=py_to_dict(body),
            model=AdminLinkUserAssignResponse
        )

    async def delete_clear_link(self, username: str) -> AdminLinkUserClearResponse:
        """
        Deletes an existing link

        Args:
            username (str): The user to unlink

        Returns:
            AdminLinkUserClearResponse: The response
        """
        return await parsed_delete_request(
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
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_HEALTH_CHECK),
            error_message="Health check failed!",
            params={},
            model=HealthCheckResponse
        )

    async def get_user_request_history(self) -> AccessRequestList:
        """
        
        Gets the users access request history

        Returns:
            AccessRequestList: The list of requests
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_USER_REQUEST_HISTORY),
            error_message="Failed to retrieve access request history.",
            params={},
            model=AccessRequestList
        )

    async def post_user_request_change(self, body: AccessReport, send_email: bool) -> StatusResponse:
        """
        
        Requests a change by diffing access models

        Args:
            body (AccessReport): The new access desired
            send_email (bool): Email alert

        Returns:
            StatusResponse: Ok?
        """
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
        """
        Gets only pending requests from history

        Returns:
            AccessRequestList: The list
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_USER_PENDING_REQUEST_HISTORY),
            error_message="Failed to retrieve access pending request history.",
            params={},
            model=AccessRequestList
        )

    async def get_user_generate_access_report(self) -> AccessReportResponse:
        """
        
        Generates an access report detailing system access.

        Returns:
            AccessReportResponse: The response
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_ACCESS_CONTROL_USER_GENERATE_ACCESS_REPORT),
            error_message="Failed to generate access report.",
            params={},
            model=AccessReportResponse
        )

    async def get_list_groups(self) -> ListGroupsResponse:
        """
        Lists all groups

        Returns:
            ListGroupsResponse: List of groups
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_LIST_GROUPS),
            error_message="Failed to list groups",
            params={},
            model=ListGroupsResponse
        )

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        """
        
        Describes a specific gruop

        Args:
            group_id (str): The id of group

        Returns:
            DescribeGroupResponse: Response with details
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_DESCRIBE_GROUP),
            error_message="Failed to describe group",
            params={'id': group_id},
            model=DescribeGroupResponse
        )

    async def get_list_membership(self) -> ListUserMembershipResponse:
        """
        
        Gets the list of groups user is member of

        Returns:
            ListUserMembershipResponse: List and details
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_LIST_USER_MEMBERSHIP),
            error_message="Failed to list group membership.",
            params={},
            model=ListUserMembershipResponse
        )

    async def get_list_group_members(self, group_id: str) -> ListMembersResponse:
        """
        
        Lists the members of a given group

        Args:
            group_id (str): The group to lookup

        Returns:
            ListMembersResponse: Members
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_LIST_MEMBERS),
            error_message="Failed to list group members",
            params={'id': group_id},
            model=ListMembersResponse
        )

    async def get_check_membership(self, group_id: str) -> CheckMembershipResponse:
        """
        Checks if user is in specific group

        Args:
            group_id (str): The group to check

        Returns:
            CheckMembershipResponse: In group?
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                AuthEndpoints.GET_GROUPS_USER_CHECK_MEMBERSHIP),
            error_message="Failed to check membership.",
            params={'id': group_id},
            model=CheckMembershipResponse
        )

    async def get_link_lookup_username(self, username: Optional[str]=None) -> UserLinkUserLookupResponse:
        """
        
        Looks up either current user or specified user

        Args:
            username (Optional[str], optional): The username if not current user. Defaults to None.

        Returns:
            UserLinkUserLookupResponse: The response indicating link
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.GET_LINK_USER_LOOKUP),
            error_message="Failed to lookup user in link service.",
            params={'username': username},
            model=UserLinkUserLookupResponse
        )

    async def post_link_assign(self, body: UserLinkUserAssignRequest) -> UserLinkUserAssignResponse:
        """
        
        Assigns link to current user.

        Args:
            body (UserLinkUserAssignRequest): The link to assign

        Returns:
            UserLinkUserAssignResponse: The response indicating success
        """
        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_LINK_USER_ASSIGN),
            error_message="Failed to assign user link.",
            params={},
            json_body=py_to_dict(body),
            model=UserLinkUserAssignResponse
        )

    async def post_link_validate(self, body: UserLinkUserAssignRequest) -> UserLinkUserValidateResponse:
        """
        Validates link before making it.

        Args:
            body (UserLinkUserAssignRequest): The link to assign

        Returns:
            UserLinkUserValidateResponse: Valid?
        """
        # Doesn't assert status as we want the status response to fall through
        # to user
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(AuthEndpoints.POST_LINK_USER_VALIDATE),
            error_message="Failed to validate user link.",
            params={},
            json_body=py_to_dict(body),
            model=UserLinkUserValidateResponse
        )
