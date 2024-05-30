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
        return await self._auth_client.admin.get_all_pending_request_history()

    async def get_all_request_history(self) -> AccessRequestList:
        return await self._auth_client.admin.get_all_request_history()

    async def get_user_pending_request_history(self, username: str) -> AccessRequestList:
        return await self._auth_client.admin.get_user_pending_request_history(username=username)

    async def get_user_request_history(self, username: str) -> AccessRequestList:
        return await self._auth_client.admin.get_user_request_history(username=username)

    async def post_add_note(self, note: RequestAddNote) -> None:
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
        return await self._auth_client.admin.get_list_groups()

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        return await self._auth_client.admin.get_describe_group(group_id=group_id)

    async def get_list_members(self, group_id: str) -> ListMembersResponse:
        return await self._auth_client.admin.get_list_members(group_id=group_id)

    async def get_list_group_membership(self, username: str) -> ListUserMembershipResponse:
        return await self._auth_client.admin.get_list_group_membership(username=username)

    async def get_check_user_membership(self, username: str, group_id: str) -> CheckMembershipResponse:
        return await self._auth_client.admin.get_check_user_membership(username=username, group_id=group_id)

    async def post_groups_add_member(self, group_id: str, user: GroupUser) -> AddMemberResponse:
        return await self._auth_client.admin.post_groups_add_member(user=user, group_id=group_id)

    async def delete_remove_member(self, group_id: str, username: str) -> RemoveMemberResponse:
        return await self._auth_client.admin.delete_remove_member(username=username, group_id=group_id)

    async def post_add_group(self, group: UserGroupMetadata) -> AddGroupResponse:
        return await self._auth_client.admin.post_add_group(group=group)

    async def put_update_group(self, group: UserGroupMetadata) -> UpdateGroupResponse:
        return await self._auth_client.admin.put_update_group(group=group)

    async def get_export_groups(self) -> GroupsExportResponse:
        return await self._auth_client.admin.get_export_groups()

    async def post_import_groups(self, body: GroupsImportRequest) -> GroupsImportResponse:
        return await self._auth_client.admin.post_import_groups(body=body)

    async def post_restore_groups_from_table(self, table_name: str, body: GroupsRestoreRequest) -> GroupsImportResponse:
        return await self._auth_client.admin.post_restore_groups_from_table(body=body, table_name=table_name)

    async def get_link_lookup_username(self, username: str) -> AdminLinkUserLookupResponse:
        return await self._auth_client.admin.get_link_lookup_username(username=username)

    async def get_link_reverse_lookup_username(self, person_id: str) -> UserLinkReverseLookupResponse:
        return await self._auth_client.admin.get_link_reverse_lookup_username(person_id=person_id)

    async def post_link_assign(self, body: AdminLinkUserAssignRequest) -> AdminLinkUserAssignResponse:
        return await self._auth_client.admin.post_link_assign(body=body)

    async def delete_clear_link(self, username: str) -> AdminLinkUserClearResponse:
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
        return await self._auth_client.get_health_check()

    async def get_user_request_history(self) -> AccessRequestList:
        return await self._auth_client.get_user_request_history()

    async def post_user_request_change(self, body: AccessReport, send_email: bool) -> StatusResponse:
        return await self._auth_client.post_user_request_change(body=body, send_email=send_email)

    async def get_user_pending_request_history(self) -> AccessRequestList:
        return await self._auth_client.get_user_pending_request_history()

    async def get_user_generate_access_report(self) -> AccessReportResponse:
        return await self._auth_client.get_user_generate_access_report()

    async def get_list_groups(self) -> ListGroupsResponse:
        return await self._auth_client.get_list_groups()

    async def get_describe_group(self, group_id: str) -> DescribeGroupResponse:
        return await self._auth_client.get_describe_group(group_id=group_id)

    async def get_list_membership(self) -> ListUserMembershipResponse:
        return await self._auth_client.get_list_membership()

    async def get_list_group_members(self, group_id: str) -> ListMembersResponse:
        return await self._auth_client.get_list_group_members(group_id=group_id)

    async def get_check_membership(self, group_id: str) -> CheckMembershipResponse:
        return await self._auth_client.get_check_membership(group_id=group_id)

    async def get_link_lookup_username(self, username: Optional[str] = None) -> UserLinkUserLookupResponse:
        return await self._auth_client.get_link_lookup_username(username=username)

    async def post_link_assign(self, body: UserLinkUserAssignRequest) -> UserLinkUserAssignResponse:
        return await self._auth_client.post_link_assign(body=body)

    async def post_link_validate(self, body: UserLinkUserAssignRequest) -> UserLinkUserValidateResponse:
        return await self._auth_client.post_link_validate(body=body)
