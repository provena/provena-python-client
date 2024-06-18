'''
Created Date: Friday May 31st 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday May 31st 2024 9:50:26 am +1000
Modified By: Peter Baker
-----
Description: Auth API L3 Module.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import AuthClient
from provenaclient.modules.module_helpers import *
from provenaclient.models import HealthCheckResponse
from ProvenaInterfaces.AuthAPI import *

# L3 interface.


class AdminAuthSubModule(ModuleService):
    _auth_client: AuthClient

    def __init__(self, auth: AuthManager, config: Config, auth_client: AuthClient) -> None:
        """
        Admin sub module of the Auth API functionality

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance. 
        auth_client: AuthClient
            The instantiated auth client
        """
        self._auth = auth
        self._config = config

        # Clients related to the datastore scoped as private.
        self._auth_client = auth_client

    async def get_all_pending_request_history(self) -> AccessRequestList:
        """

        Gets all requests with pending status

        Returns:
            AccessRequestList: The response object
        """
        return await self._auth_client.admin.get_all_pending_request_history()

    async def get_all_request_history(self) -> AccessRequestList:
        """

        Gets all requests

        Returns:
            AccessRequestList: The response object
        """
        return await self._auth_client.admin.get_all_request_history()

    async def get_user_pending_request_history(self, username: str) -> AccessRequestList:
        """

        Gets pending requests for specified user

        Args:
            username (str): Username to query

        Returns:
            AccessRequestList: The response list
        """
        return await self._auth_client.admin.get_user_pending_request_history(username=username)

    async def get_user_request_history(self, username: str) -> AccessRequestList:
        """

        Gets all requests for specified user

        Args:
            username (str): Username to query

        Returns:
            AccessRequestList: The response list
        """
        return await self._auth_client.admin.get_user_request_history(username=username)

    async def post_add_note(self, note: RequestAddNote) -> None:
        """
        Adds a note to an existing request

        Args:
            note (RequestAddNote): Payload incl note info
        """
        return await self._auth_client.admin.post_add_note(
            note=note
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
        return await self._auth_client.admin.post_change_request_state(
            change=change,
            send_email_alert=send_email_alert
        )

    async def get_list_groups(self) -> ListGroupsResponse:
        """
        
        Gets a list of groups

        Returns:
            ListGroupsResponse: List of groups
        """
        return await self._auth_client.admin.get_list_groups()

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        """
        
        Describes a group by ID

        Args:
            group_id (str): The group

        Returns:
            DescribeGroupResponse: Description
        """
        return await self._auth_client.admin.get_describe_group(group_id=group_id)

    async def get_list_members(self, group_id: str) -> ListMembersResponse:
        """
        Lists members of group

        Args:
            group_id (str): The gruop

        Returns:
            ListMembersResponse: The list of members
        """
        return await self._auth_client.admin.get_list_members(group_id=group_id)

    async def get_list_group_membership(self, username: str) -> ListUserMembershipResponse:
        """
        
        Gets list of groups a user is in

        Args:
            username (str): The username

        Returns:
            ListUserMembershipResponse: The list of groups
        """
        return await self._auth_client.admin.get_list_group_membership(username=username)

    async def get_check_user_membership(self, username: str, group_id: str) -> CheckMembershipResponse:
        """
        
        Checks user membership within a group

        Args:
            username (str): The username to target
            group_id (str): The group to check

        Returns:
            CheckMembershipResponse: Response
        """
        return await self._auth_client.admin.get_check_user_membership(username=username, group_id=group_id)

    async def post_groups_add_member(self, group_id: str, user: GroupUser) -> AddMemberResponse:
        """
        
        Adds a member to a group

        Args:
            group_id (str): Id of group
            user (GroupUser): The user to add

        Returns:
            AddMemberResponse: The response
        """
        return await self._auth_client.admin.post_groups_add_member(user=user, group_id=group_id)

    async def delete_remove_member(self, group_id: str, username: str) -> RemoveMemberResponse:
        """
        
        Removes member from group

        Args:
            group_id (str): The id of group
            username (str): The user to remove

        Returns:
            RemoveMemberResponse: The response
        """
        return await self._auth_client.admin.delete_remove_member(username=username, group_id=group_id)

    async def post_add_group(self, group: UserGroupMetadata) -> AddGroupResponse:
        """
        
        Adds a group/creates group

        Args:
            group (UserGroupMetadata): The group details

        Returns:
            AddGroupResponse: The response
        """
        return await self._auth_client.admin.post_add_group(group=group)

    async def put_update_group(self, group: UserGroupMetadata) -> UpdateGroupResponse:
        """
        Updates group details

        Args:
            group (UserGroupMetadata): The group metadata

        Returns:
            UpdateGroupResponse: The response
        """
        return await self._auth_client.admin.put_update_group(group=group)

    async def get_export_groups(self) -> GroupsExportResponse:
        """
        Exports all group details in specified format.

        Returns:
            GroupsExportResponse: The data dump
        """
        return await self._auth_client.admin.get_export_groups()

    async def post_import_groups(self, body: GroupsImportRequest) -> GroupsImportResponse:
        """
        
        Imports groups from data dump back in

        Args:
            body (GroupsImportRequest): The import request incl. dump

        Returns:
            GroupsImportResponse: The response
        """
        return await self._auth_client.admin.post_import_groups(body=body)

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
        return await self._auth_client.admin.post_restore_groups_from_table(body=body, table_name=table_name)

    async def get_link_lookup_username(self, username: str) -> AdminLinkUserLookupResponse:
        """
        Gets the linked person for user

        Args:
            username (str): User to lookup

        Returns:
            AdminLinkUserLookupResponse: Response
        """
        return await self._auth_client.admin.get_link_lookup_username(username=username)

    async def get_link_reverse_lookup_username(self, person_id: str) -> UserLinkReverseLookupResponse:
        """
        
        Looks up reverse by person ID

        Args:
            person_id (str): The person to lookup

        Returns:
            UserLinkReverseLookupResponse: The response
        """
        return await self._auth_client.admin.get_link_reverse_lookup_username(person_id=person_id)

    async def post_link_assign(self, body: AdminLinkUserAssignRequest) -> AdminLinkUserAssignResponse:
        """
        
        Assigns a person to a given user

        Args:
            body (AdminLinkUserAssignRequest): The request

        Returns:
            AdminLinkUserAssignResponse: The response
        """
        return await self._auth_client.admin.post_link_assign(body=body)

    async def delete_clear_link(self, username: str) -> AdminLinkUserClearResponse:
        """
        Deletes an existing link

        Args:
            username (str): The user to unlink

        Returns:
            AdminLinkUserClearResponse: The response
        """
        return await self._auth_client.admin.delete_clear_link(username=username)


class Auth(ModuleService):
    # Internal clients
    _auth_client: AuthClient

    # Sub Modules
    admin: AdminAuthSubModule

    def __init__(self, auth: AuthManager, config: Config, auth_client: AuthClient) -> None:
        """

        Sets up the auth API L3 module. 

        Includes admin sub module.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance. 
        """
        self._auth = auth
        self._config = config

        # Clients related to the datastore scoped as private.
        self._auth_client = auth_client

        # Sub Modules
        self.admin = AdminAuthSubModule(
            auth=self._auth,
            config=self._config,
            auth_client=self._auth_client
        )

    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await self._auth_client.get_health_check()

    async def get_user_request_history(self) -> AccessRequestList:
        """
        
        Gets the users access request history

        Returns:
            AccessRequestList: The list of requests
        """
        return await self._auth_client.get_user_request_history()

    async def post_user_request_change(self, body: AccessReport, send_email: bool) -> StatusResponse:
        """
        
        Requests a change by diffing access models

        Args:
            body (AccessReport): The new access desired
            send_email (bool): Email alert

        Returns:
            StatusResponse: Ok?
        """
        return await self._auth_client.post_user_request_change(body=body, send_email=send_email)

    async def get_user_pending_request_history(self) -> AccessRequestList:
        """
        Gets only pending requests from history

        Returns:
            AccessRequestList: The list
        """
        return await self._auth_client.get_user_pending_request_history()

    async def get_user_generate_access_report(self) -> AccessReportResponse:
        """
        
        Generates an access report detailing system access.

        Returns:
            AccessReportResponse: The response
        """
        return await self._auth_client.get_user_generate_access_report()

    async def get_list_groups(self) -> ListGroupsResponse:
        """
        Lists all groups

        Returns:
            ListGroupsResponse: List of groups
        """
        return await self._auth_client.get_list_groups()

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        """
        
        Describes a specific gruop

        Args:
            group_id (str): The id of group

        Returns:
            DescribeGroupResponse: Response with details
        """
        return await self._auth_client.get_describe_group(group_id=group_id)

    async def get_list_membership(self) -> ListUserMembershipResponse:
        """
        
        Gets the list of groups user is member of

        Returns:
            ListUserMembershipResponse: List and details
        """
        return await self._auth_client.get_list_membership()

    async def get_list_group_members(self, group_id: str) -> ListMembersResponse:
        """
        
        Lists the members of a given group

        Args:
            group_id (str): The group to lookup

        Returns:
            ListMembersResponse: Members
        """
        return await self._auth_client.get_list_group_members(group_id=group_id)

    async def get_check_membership(self, group_id: str) -> CheckMembershipResponse:
        """
        Checks if user is in specific group

        Args:
            group_id (str): The group to check

        Returns:
            CheckMembershipResponse: In group?
        """
        return await self._auth_client.get_check_membership(group_id=group_id)

    async def get_link_lookup_username(self, username: Optional[str] = None) -> UserLinkUserLookupResponse:
        """
        
        Looks up either current user or specified user

        Args:
            username (Optional[str], optional): The username if not current user. Defaults to None.

        Returns:
            UserLinkUserLookupResponse: The response indicating link
        """
        return await self._auth_client.get_link_lookup_username(username=username)

    async def post_link_assign(self, body: UserLinkUserAssignRequest) -> UserLinkUserAssignResponse:
        """
        
        Assigns link to current user.

        Args:
            body (UserLinkUserAssignRequest): The link to assign

        Returns:
            UserLinkUserAssignResponse: The response indicating success
        """
        return await self._auth_client.post_link_assign(body=body)

    async def post_link_validate(self, body: UserLinkUserAssignRequest) -> UserLinkUserValidateResponse:
        """
        Validates link before making it.

        Args:
            body (UserLinkUserAssignRequest): The link to assign

        Returns:
            UserLinkUserValidateResponse: Valid?
        """
        return await self._auth_client.post_link_validate(body=body)
