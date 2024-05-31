from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.modules.module_helpers import *
from provenaclient.clients import RegistryClient
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from typing import Optional


# L3 interface.


class OrganisationClient(ModuleService):
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

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> OrganisationFetchResponse:
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.ORGANISATION,
            fetch_response_model=OrganisationFetchResponse,
            seed_allowed=seed_allowed
        )

    async def update(self, id: str, domain_info: OrganisationDomainInfo, reason: Optional[str]) -> StatusResponse:
        return await self._registry_client.update_item(
            id=id,
            item_subtype=ItemSubType.ORGANISATION,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )


class ModelClient(ModuleService):
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

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> ModelFetchResponse:
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.MODEL,
            fetch_response_model=ModelFetchResponse,
            seed_allowed=seed_allowed
        )
        
    async def update(self, id: str, domain_info: ModelDomainInfo, reason: Optional[str]) -> StatusResponse:
        return await self._registry_client.update_item(
            id=id,
            item_subtype=ItemSubType.MODEL,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )


class Registry(ModuleService):
    # L2 clients used
    _registry_client: RegistryClient

    # Sub modules
    organisation: OrganisationClient
    model: ModelClient

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

        # Sub modules
        self.organisation = OrganisationClient(
            auth=auth, config=config, registry_client=registry_client)
        self.model = ModelClient(
            auth=auth, config=config, registry_client=registry_client)
