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
        """
        Fetches an organisation from the registry

        Args:
            id (str): The organisation ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            OrganisationFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.ORGANISATION,
            fetch_response_model=OrganisationFetchResponse,
            seed_allowed=seed_allowed
        )

    async def update(self, id: str, domain_info: OrganisationDomainInfo, reason: Optional[str]) -> StatusResponse:
        """
        Updates an organisation in the registry

        Args:
            id (str): The id of the organisation
            domain_info (OrganisationDomainInfo): The new domain info
            reason (Optional[str]): The reason if any

        Returns:
            StatusResponse: Status response
        """
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
        """
        Fetches a model from the registry

        Args:
            id (str): The model ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            ModelFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.MODEL,
            fetch_response_model=ModelFetchResponse,
            seed_allowed=seed_allowed
        )
        
    async def update(self, id: str, domain_info: ModelDomainInfo, reason: Optional[str]) -> StatusResponse:
        """
        Updates a model in the registry

        Args:
            id (str): The id of the model
            domain_info (ModelDomainInfo): The new domain info
            reason (Optional[str]): The reason if any

        Returns:
            StatusResponse: Status response
        """
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
