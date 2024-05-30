from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import AuthClient
from provenaclient.modules.module_helpers import *
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
        return await self._auth_client.admin.post_change_request_state(
            send_email_alert=send_email_alert,
            change=change
        )


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
