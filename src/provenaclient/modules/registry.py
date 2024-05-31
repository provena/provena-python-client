from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from pydantic import BaseModel
from provenaclient.modules.module_helpers import *
from provenaclient.clients import RegistryClient


# L3 interface.

class Registry(ModuleService):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance.
        """
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the registry scoped as private.
        self._registry_client = registry_client

