'''
Created Date: Thursday June 6th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday June 6th 2024 1:39:55 pm +1000
Modified By: Peter Baker
-----
Description: Registry API L3 module.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Initial proof of concept with fetch/update methods from L2. Sub Modules for each subtype.
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.models.general import HealthCheckResponse
from provenaclient.utils.config import Config
from provenaclient.modules.module_helpers import *
from provenaclient.clients import RegistryClient
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from typing import Optional


# L3 interface.

class RegistryAdminClient(ModuleService):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Admin sub module of the Registry API providing functionality
        for the admin endpoints.

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

        # Clients related to the registry_api scoped as private.
        self._registry_client = registry_client

    
    async def delete(self, id: str, item_subtype: ItemSubType) -> StatusResponse:

        return await self._registry_client.admin.delete_item(
            id = id, 
            item_subtype=item_subtype
        )

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
    
    async def create(self, item_info: OrganisationDomainInfo)


class CreateActivityClient(ModuleService):
    
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
        Fetches a create activity item from the registry

        Args:
            id (str): The model ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            ModelFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.CREATE,
            fetch_response_model=ModelFetchResponse,
            seed_allowed=seed_allowed
        )


class VersionActivityClient(ModuleService):

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
        Fetches a version item from the registry

        Args:
            id (str): The model ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            ModelFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.VERSION,
            fetch_response_model=ModelFetchResponse,
            seed_allowed=seed_allowed
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
    create_activity: CreateActivityClient
    version_acitvity: VersionActivityClient
    admin: RegistryAdminClient

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
        self.create_activity = CreateActivityClient(
            auth=auth, config=config, registry_client=registry_client)
        self.version_acitvity = VersionActivityClient(
            auth=auth, config=config, registry_client=registry_client)
        self.admin = RegistryAdminClient(
            auth=auth, config=config, registry_client=registry_client
        )
    
    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await self._registry_client.get_health_check()
        
