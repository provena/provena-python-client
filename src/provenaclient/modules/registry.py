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

12-07-2024 | Parth Kulkarni | Adding some useful L3 methods to retrieve summarized info of registry items. 
28-06-2024 | Parth Kulkarni | Completion of Registry L3 interface with General, Admin and Other endpoints. 
18-06-2024 | Peter Baker | Initial proof of concept with fetch/update methods from L2. Sub Modules for each subtype.

'''

from ProvenaInterfaces.RegistryAPI import Any, DomainInfoBase
from ProvenaInterfaces.RegistryModels import Any, DomainInfoBase
from provenaclient.auth.manager import AuthManager
from provenaclient.models.general import HealthCheckResponse
from provenaclient.utils.config import Config
from provenaclient.modules.module_helpers import *
from provenaclient.clients import RegistryClient
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from typing import Optional
from provenaclient.utils.helpers import convert_to_item_subtype, write_file_helper, get_and_validate_file_path
from abc import abstractmethod


DEFAULT_CONFIG_FILE_NAME = "registry-api.env"

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

    
    async def export_items(self) -> RegistryExportResponse:
        """Provides a mechanism for admins to dump the current contents of the registry table without any validation/parsing.
        
        Returns
        -------
        RegistryExportResponse
            A status response including items in the payload
        """

        return await self._registry_client.admin.export_items()
    
    async def import_items(self, registry_import_request: RegistryImportRequest) -> RegistryImportResponse:
        """This admin only endpoint enables rapid restoration of items in into the registry table.

        Parameters
        ----------
        registry_import_request : RegistryImportRequest
            Contains the import mode, more info can be found on API docs.

        Returns
        -------
        RegistryImportResponse
            Returns an import response which includes status + statistics.
        """

        return await self._registry_client.admin.import_items(
            registry_import_request=registry_import_request
        )
    
    async def restore_items_from_dynamo_table(self, restore_request: RegistryRestoreRequest) -> RegistryImportResponse:
        """Provides an admin only mechanism for copying/restoring the contents from another dynamoDB table into the currently active registry table. 
        This endpoint does not create any new tables - it just uses the items from a restored table (e.g. from a backup) as inputs to an import operation 
        against the current registry table.

        Parameters
        ----------
        restore_request : RegistryRestoreRequest
            The restore request settings - these will be used when propagating the items from the external table.

        Returns
        -------
        RegistryImportResponse
            Returns information about the import, including status and statistics.
        """

        return await self._registry_client.admin.restore_items_from_dynamo_table(
            restore_request=restore_request
        )
    
    async def generate_config_file(self, required_only: bool = True, file_path: Optional[str] = None, write_to_file: bool = False) -> str:
        """Generates a nicely formatted .env file of the current required/non supplied properties 
        Used to quickly bootstrap a local environment or to understand currently deployed API.

        Parameters
        ----------
        required_only : bool, optional
            By default True
        file_path: str, optional
            The path you want to save the config file at WITH the file name. If you don't specify a path
            this will be saved in a relative directory.
        write_to_file: bool, By default False
            A boolean flag to indicate whether you want to save the config response to a file
            or not.

        Returns
        ----------
        str: Response containing the config text.

        """

        file_path = get_and_validate_file_path(file_path=file_path, write_to_file=write_to_file, default_file_name=DEFAULT_CONFIG_FILE_NAME)

        config_text: str = await self._registry_client.admin.generate_config_file(required_only=required_only)

        if config_text is None:
            raise ValueError(f"No data returned for generate config file endpoint.")

        # Write to file if config text is not None, write to file is True and file path is not None.
        if write_to_file:
            if file_path is None:
                raise ValueError("File path is not set for writing the CSV.")
            write_file_helper(file_path=file_path, content=config_text)

        return config_text
    
    async def delete(self, id: str, item_subtype: Optional[ItemSubType] = None) -> StatusResponse:
        """Admin only endpoint for deleting item from registry. USE CAREFULLY!

        Parameters
        ----------
        id : str
            ID of entity/item you want to delete.
        item_subtype : Optional[ItemSubType]
            Subtype of item you want to delete (E.g ORGANISATION, PERSON, CREATE)
            If not provided, it will be fetched from the registry.

        Returns
        -------
        StatusResponse
            Response indicating the success/failure of your request.
        """

        if item_subtype is None: 
            fetch_item = await self._registry_client.general.general_fetch_item(id=id)
            
            if fetch_item.item: 
                item_subtype_str: Optional[str] = fetch_item.item.get("item_subtype")
                item_subtype = convert_to_item_subtype(item_subtype_str)
            else:
                raise ValueError("Item not found")
                        
        return await self._registry_client.admin.delete_item(
            id = id, 
            item_subtype=item_subtype
        )
    
    
class RegistryBaseClass(ModuleService):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient, item_subtype: ItemSubType) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        item_subtype : ItemSubType
            The subtype of the item (e.g., ORGANISATION, PERSON).
        """
        self._auth = auth
        self._config = config
        self._registry_client = registry_client
        self.item_subtype = item_subtype

    
    async def admin_delete(self, id: str) -> StatusResponse:
        """Admin only endpoint for deleting item from registry. USE CAREFULLY!

        Parameters
        ----------
        id : str
            ID of entity/item you want to delete.

        Returns
        -------
        StatusResponse
            Response indicating the success/failure of your request.
        """

        return await self._registry_client.admin.delete_item(
            id = id, 
            item_subtype=self.item_subtype
        )

    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:
        """
        Reverts an item in the registry based on item subtype.

        Parameters
        ----------
        revert_request : ItemRevertRequest
            The revert request

        Returns
        -------
        ItemRevertResponse
            The revert response
        """
        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=self.item_subtype
        )
    
    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for the item subtype

        Returns
        -------
        JsonSchemaResponse
            The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=self.item_subtype
        )
    
    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for an item based on item subtype.

        Parameters
        ----------
        id : str
            The item ID

        Returns
        -------
        DescribeAccessResponse
            The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id, 
            item_subtype=self.item_subtype
        )
    
    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for an item based on item subtype.

        Parameters
        ----------
        id : str
            The item ID

        Returns
        -------
        AccessSettings
            The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=self.item_subtype
        )
    
    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for an item based on item subtype.

        Parameters
        ----------
        id : str
            The item ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse
            The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=self.item_subtype
        )
    
    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for the item subtype.

        Returns
        -------
        AuthRolesResponse
            The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=self.item_subtype
        )
    
    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a resource in the registry based on item subtype.

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse
            The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=self.item_subtype
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a resource in the registry based on item subtype.

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse
            The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=self.item_subtype
        )
    
    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for an item based on item subtype.

        Parameters
        ----------
        id : str
            The item ID

        Returns
        -------
        LockHistoryResponse
            The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=self.item_subtype
        )
    
    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for an item based on item subtype.

        Parameters
        ----------
        id : str
            The item ID

        Returns
        -------
        LockStatusResponse
            The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=self.item_subtype
        )
    
class OrganisationClient(RegistryBaseClass):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        """
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.ORGANISATION)

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
            item_subtype=self.item_subtype,
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
            item_subtype=self.item_subtype,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> OrganisationListResponse:
        """
        Lists all organisations within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria

        Returns
        -------
        OrganisationListResponse: The list response
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype, 
            update_model_response=OrganisationListResponse
        )

    async def seed_item(self) -> OrganisationSeedResponse:
        """
        Seeds an organisation in the registry

        Returns
        -------
        OrganisationSeedResponse: The seed response
        """
        return await self._registry_client.seed_item(
            item_subtype=self.item_subtype,
            seed_model_response=OrganisationSeedResponse
        )

    async def create_item(self, create_item_request: OrganisationDomainInfo) -> OrganisationCreateResponse:
        """
        Creates an organisation in the registry

        Parameters
        ----------
        create_item_request : OrganisationDomainInfo
            The create item request

        Returns
        -------
        OrganisationCreateResponse: The create response
        """
        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=self.item_subtype,
            create_response_model=OrganisationCreateResponse
        )

    async def validate_item(self, validate_request: OrganisationDomainInfo) -> StatusResponse:
        """
        Validates an organisation in the registry

        Parameters
        ----------
        validate_request : OrganisationDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    

class PersonClient(RegistryBaseClass):
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
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.PERSON)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> PersonFetchResponse:
        """
        Fetches a person from the registry

        Args:
            id (str): The person ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            PersonFetch: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=PersonFetchResponse,
            seed_allowed=seed_allowed
        )

    async def update(self, id: str, domain_info: PersonDomainInfo, reason: Optional[str]) -> StatusResponse:
        """
        Updates a person in the registry

        Args:
            id (str): The id of the organisation
            domain_info (OrganisationDomainInfo): The new domain info
            reason (Optional[str]): The reason if any

        Returns:
            StatusResponse: Status response
        """
        return await self._registry_client.update_item(
            id=id,
            item_subtype=self.item_subtype,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )
    
    async def list_items(self, list_items_payload: GeneralListRequest) -> PersonListResponse:
        """Lists all person(s) within registry based on filter
        criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload contaning the filter/sort criteria
        """

        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype, 
            update_model_response=PersonListResponse
        )
    
    async def seed_item(self) -> PersonSeedResponse:
        """
        Seeds a person in the registry

        Returns
        -------
        PersonSeedResponse: The seed response
        """

        return await self._registry_client.seed_item(
            item_subtype=self.item_subtype,
            seed_model_response=PersonSeedResponse
        )
    
    async def create_item(self, create_item_request: PersonDomainInfo) -> PersonCreateResponse:
        """
        Creates a person in the registry

        Parameters
        ----------
        create_item_request : OrganisationDomainInfo
            The create item request

        Returns
        -------
        PersonCreateResponse: The create response
        """

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=self.item_subtype,
            create_response_model=PersonCreateResponse
        )
    
    async def validate_item(self, validate_request: PersonDomainInfo) -> StatusResponse:
        """
        Validates a person in the registry

        Parameters
        ----------
        validate_request : PersonDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    

class CreateActivityClient(RegistryBaseClass):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        """
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.CREATE)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> CreateFetchResponse:
        """
        Fetches a create activity item from the registry

        Args:
            id (str): The create activity item ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            CreateFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=CreateFetchResponse,
            seed_allowed=seed_allowed
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> CreateListResponse:
        """
        Lists all create activity items within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria

        Returns
        -------
        CreateListResponse: The list response
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=CreateListResponse
        )
    
    async def validate_item(self, validate_request: CreateDomainInfo) -> StatusResponse:
        """
        Validates a create-item activity in the registry

        Parameters
        ----------
        validate_request : CreateDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    
    async def create_item(self, create_item_request: DomainInfoBase) -> Any:
        pass



class VersionActivityClient(RegistryBaseClass):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        """
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.VERSION)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> VersionFetchResponse:
        """
        Fetches a version activity item from the registry

        Args:
            id (str): The version activity item ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            VersionFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=VersionFetchResponse,
            seed_allowed=seed_allowed
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> VersionListResponse:
        """
        Lists all version activity items within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria

        Returns
        -------
        VersionListResponse: The list response
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=VersionListResponse
        )
    
    async def validate_item(self, validate_request: VersionDomainInfo) -> StatusResponse:
        """
        Validates a version activity in the registry

        Parameters
        ----------
        validate_request : VersionDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    

class ModelRunActivityClient(RegistryBaseClass):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        """
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.MODEL_RUN)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> ModelRunFetchResponse:
        """
        Fetches a model run activity item from the registry

        Args:
            id (str): The model run activity item ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            ModelRunFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=ModelRunFetchResponse,
            seed_allowed=seed_allowed
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> ModelRunListResponse:
        """
        Lists all model run activity items within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria

        Returns
        -------
        ModelRunListResponse: The list response
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=ModelRunListResponse
        )
    
    async def validate_item(self, validate_request: ModelRunDomainInfo) -> StatusResponse:
        """
        Validates a model run in the registry

        Parameters
        ----------
        validate_request : ModelRunDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    

    
class ModelClient(RegistryBaseClass):
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

        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.MODEL)

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
            item_subtype=self.item_subtype,
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
            item_subtype=self.item_subtype,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )
    
    async def list_items(self, list_items_payload: GeneralListRequest) -> ModelListResponse:
        """Lists all model(s) within registry based on filter
        criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload contaning the filter/sort criteria
        """

        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype, 
            update_model_response=ModelListResponse
        )
    
    async def seed_item(self) -> ModelSeedResponse:
        """
        Seeds a model in the registry

        Returns
        -------
        ModelSeedResponse: The seed response
        """

        return await self._registry_client.seed_item(
            item_subtype=self.item_subtype,
            seed_model_response=ModelSeedResponse
        )
    
    
    async def create_item(self, create_item_request: ModelDomainInfo) -> ModelCreateResponse:
        """
        Creates a model in the registry

        Parameters
        ----------
        create_item_request : ModelDomainInfo
            The create item request

        Returns
        -------
        ModelCreateResponse: The create response
        """

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=self.item_subtype,
            create_response_model=ModelCreateResponse
        )
    
    async def validate_item(self, validate_request: ModelDomainInfo) -> StatusResponse:
        """
        Validates a model item in the registry

        Parameters
        ----------
        validate_request : ModelDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    
     
    async def version_item(self, version_request: VersionRequest) -> VersionResponse:
        """
        Versions a model in the registry

        Parameters
        ----------
        version_request : VersionRequest
            The version request

        Returns
        -------
        VersionResponse: The version response
        """

        return await self._registry_client.version(
            version_request=version_request,
            item_subtype=self.item_subtype
        )
    
class ModelRunWorkFlowClient(RegistryBaseClass):
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
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> ModelRunWorkflowTemplateFetchResponse:
        """
        Fetches a model run workflow template from the registry

        Args:
            id (str): The model run workflow template ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            ModelFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=ModelRunWorkflowTemplateFetchResponse,
            seed_allowed=seed_allowed
        )
        
    async def update(self, id: str, domain_info: ModelRunWorkflowTemplateDomainInfo, reason: Optional[str]) -> StatusResponse:
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
            item_subtype=self.item_subtype,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )
    
    async def list_items(self, list_items_payload: GeneralListRequest) -> ModelRunWorkflowTemplateListResponse:
        """Lists all model(s) within registry based on filter
        criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload contaning the filter/sort criteria
        """

        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=ModelRunWorkflowTemplateListResponse
        )
    
    async def seed_item(self) -> ModelRunWorkflowTemplateSeedResponse:
        """
        Seeds a model run workflow template in the registry

        Returns
        -------
        ModelRunWorkflowTemplateSeedResponse: The seed response
        """

        return await self._registry_client.seed_item(
            item_subtype=self.item_subtype,
            seed_model_response=ModelRunWorkflowTemplateSeedResponse
        )
    
    
    async def create_item(self, create_item_request: ModelRunWorkflowTemplateDomainInfo) -> ModelRunWorkflowTemplateCreateResponse:
        """
        Creates a model run workflow template in the registry

        Parameters
        ----------
        create_item_request : ModelRunWorkflowTemplateDomainInfo
            The create item request

        Returns
        -------
        ModelRunWorkflowTemplateCreateResponse: The create response
        """

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=self.item_subtype,
            create_response_model=ModelRunWorkflowTemplateCreateResponse
        )
    
    async def validate_item(self, validate_request: ModelRunWorkflowTemplateDomainInfo) -> StatusResponse:
        """
        Validates a model run workflow template item in the registry

        Parameters
        ----------
        validate_request : ModelRunWorkflowTemplateDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )
    
    async def version_item(self, version_request: VersionRequest) -> VersionResponse:
        """
        Versions a model run workflow template in the registry

        Parameters
        ----------
        version_request : VersionRequest
            The version request

        Returns
        -------
        VersionResponse: The version response
        """

        return await self._registry_client.version(
            version_request=version_request,
            item_subtype=self.item_subtype
        )
    

class DatasetTemplateClient(RegistryBaseClass):
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
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.DATASET_TEMPLATE)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> DatasetTemplateFetchResponse:
        """
        Fetches a dataset template from the registry

        Args:
            id (str): The dataset template ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            DatasetTemplateFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=DatasetTemplateFetchResponse,
            seed_allowed=seed_allowed
        )

    async def update(self, id: str, domain_info: DatasetTemplateDomainInfo, reason: Optional[str]) -> StatusResponse:
        """
        Updates a dataset template in the registry

        Args:
            id (str): The id of the dataset template
            domain_info (DatasetTemplateDomainInfo): The new domain info
            reason (Optional[str]): The reason if any

        Returns:
            StatusResponse: Status response
        """
        return await self._registry_client.update_item(
            id=id,
            item_subtype=self.item_subtype,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> DatasetTemplateListResponse:
        """
        Lists all dataset templates within the registry based on filter
        criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=DatasetTemplateListResponse
        )

    async def seed_item(self) -> DatasetTemplateSeedResponse:
        """
        Seeds a dataset template in the registry

        Returns
        -------
        DatasetTemplateSeedResponse: The seed response
        """
        return await self._registry_client.seed_item(
            item_subtype=self.item_subtype,
            seed_model_response=DatasetTemplateSeedResponse
        )

    async def create_item(self, create_item_request: DatasetTemplateDomainInfo) -> DatasetTemplateCreateResponse:
        """
        Creates a dataset template in the registry

        Parameters
        ----------
        create_item_request : DatasetTemplateDomainInfo
            The create item request

        Returns
        -------
        DatasetTemplateCreateResponse: The create response
        """
        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=self.item_subtype,
            create_response_model=DatasetTemplateCreateResponse
        )
    
    async def validate_item(self, validate_request: DatasetTemplateDomainInfo) -> StatusResponse:
        """
        Validates a dataset template item in the registry

        Parameters
        ----------
        validate_request : DatasetTemplateDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )

    async def version_item(self, version_request: VersionRequest) -> VersionResponse:
        """
        Versions a dataset template in the registry

        Parameters
        ----------
        version_request : VersionRequest
            The version request

        Returns
        -------
        VersionResponse: The version response
        """
        return await self._registry_client.version(
            version_request=version_request,
            item_subtype=self.item_subtype
        )


class DatasetClient(RegistryBaseClass):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        """
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.DATASET)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> DatasetFetchResponse:
        """
        Fetches a dataset from the registry

        Args:
            id (str): The dataset ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            DatasetFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=DatasetFetchResponse,
            seed_allowed=seed_allowed
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> DatasetListResponse:
        """
        Lists all datasets within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria

        Returns
        -------
        DatasetListResponse: The list response
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=DatasetListResponse
        )
    

    async def validate_item(self, validate_request: DatasetDomainInfo) -> StatusResponse:
        """
        Validates a dataset item in the registry

        Parameters
        ----------
        validate_request : DatasetDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )


class StudyClient(RegistryBaseClass):
    _registry_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, registry_client: RegistryClient) -> None:
        """
        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        registry_client : RegistryClient
            The registry client to use for registry interactions.
        """
        
        super().__init__(auth=auth, config=config, registry_client=registry_client, item_subtype=ItemSubType.STUDY)

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> StudyFetchResponse:
        """
        Fetches a study from the registry

        Args:
            id (str): The study ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            StudyFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=self.item_subtype,
            fetch_response_model=StudyFetchResponse,
            seed_allowed=seed_allowed
        )

    async def list_items(self, list_items_payload: GeneralListRequest) -> StudyListResponse:
        """
        Lists all studies within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload containing the filter/sort criteria

        Returns
        -------
        StudyListResponse: The list response
        """
        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=self.item_subtype,
            update_model_response=StudyListResponse
        )

    async def seed_item(self) -> StudySeedResponse:
        """
        Seeds a study in the registry

        Returns
        -------
        StudySeedResponse: The seed response
        """
        return await self._registry_client.seed_item(
            item_subtype=self.item_subtype,
            seed_model_response=StudySeedResponse
        )

    async def update(self, id: str, domain_info: StudyDomainInfo, reason: Optional[str]) -> StatusResponse:
        """
        Updates a study in the registry

        Parameters
        ----------
        id : str
            The id of the study
        domain_info : StudyDomainInfo
            The new domain info
        reason : Optional[str]
            The reason, if any

        Returns
        -------
        StatusResponse: Status response
        """
        return await self._registry_client.update_item(
            id=id,
            item_subtype=self.item_subtype,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )

    async def create_item(self, create_item_request: StudyDomainInfo) -> StudyCreateResponse:
        """
        Creates a study in the registry

        Parameters
        ----------
        create_item_request : StudyDomainInfo
            The create item request

        Returns
        -------
        StudyCreateResponse: The create response
        """
        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=self.item_subtype,
            create_response_model=StudyCreateResponse
        )
    
    async def validate_item(self, validate_request: StudyDomainInfo) -> StatusResponse:
        """
        Validates a study item in the registry

        Parameters
        ----------
        validate_request : StudyDomainInfo
            The validate request

        Returns
        -------
        StatusResponse: The status response
        """

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=self.item_subtype
        )

    
class Registry(ModuleService):
    # L2 clients used
    _registry_client: RegistryClient

    # Admin sub module
    admin: RegistryAdminClient

    # Sub modules
    organisation: OrganisationClient
    person: PersonClient
    model: ModelClient
    model_run_workflow: ModelRunWorkFlowClient
    dataset_template: DatasetTemplateClient
    dataset: DatasetClient
    study: StudyClient
    create_activity: CreateActivityClient
    version_acitvity: VersionActivityClient
    model_run: ModelRunActivityClient
    
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

        # Admin sub module
        self.admin = RegistryAdminClient(
            auth=auth, config=config, registry_client=registry_client
        )

        # Sub modules
        self.organisation = OrganisationClient(
            auth=auth, config=config, registry_client=registry_client)    
        self.person = PersonClient(
            auth=auth, config=config, registry_client=registry_client
        )
        self.model = ModelClient(
            auth=auth, config=config, registry_client=registry_client)
        self.model_run_workflow = ModelRunWorkFlowClient(
            auth=auth, config=config, registry_client=registry_client
        )
        self.dataset_template = DatasetTemplateClient(
            auth=auth, config=config, registry_client=registry_client
        )
        self.study = StudyClient(
            auth=auth, config=config, registry_client=registry_client
        )
        self.create_activity = CreateActivityClient(
            auth=auth, config=config, registry_client=registry_client)
        self.version_acitvity = VersionActivityClient(
            auth=auth, config=config, registry_client=registry_client)
        self.model_run = ModelRunActivityClient(
            auth=auth, config=config, registry_client=registry_client
        )
    
    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await self._registry_client.get_health_check()
    

    async def list_general_registry_items(self, general_list_request: GeneralListRequest) -> PaginatedListResponse:
        """
        Lists general registry items based on filter criteria.

        Parameters
        ----------
        general_list_request : GeneralListRequest
            The request containing filter and sort criteria.

        Returns
        -------
        PaginatedListResponse
            The response containing the paginated list of registry items.
        """

        return await self._registry_client.general.list_general_registry_items(
            general_list_request=general_list_request
        )
    
    async def list_registry_items_with_count(self) -> Dict[str, int]:
        """
        Retrieves a count of items in the registry, grouped by their subtypes.

        This method sends requests to list items in the registry and counts the number of items for each subtype.
        It handles pagination to ensure all items are counted.

        Returns
        -------
        Dict[str, int]
            A dictionary where the keys are item subtypes(string) and the values are the count of items for each subtype.
        """
    
        item_count: Dict[str, int] = {}

        general_list_request = GeneralListRequest(
            filter_by=FilterOptions(
                record_type=QueryRecordTypes.COMPLETE_ONLY,
                item_subtype=None, 
                release_reviewer=None,
                release_status=None
            ),
            sort_by=SortOptions(sort_type=None, ascending=False, begins_with=None),
            pagination_key=None, 
            page_size=20
        )

        while True:
            list_response = await self.list_general_registry_items(general_list_request=general_list_request)

            assert list_response.items is not None, f"Expected a list of items but none was present."

            for item in list_response.items:
                subtype: str = item.get("item_subtype")

                if not subtype:
                    unknown = "UNKNOWN"
    
                    if unknown not in item_count:
                        item_count[unknown] = 1
                    
                    else:
                        item_count[unknown] += 1
                    
                    continue  # Skip this current iteration if subtype is missing

                if subtype not in item_count:
                    item_count[subtype] = 1
                else:
                    item_count[subtype] += 1

            if not list_response.pagination_key:
                break

            general_list_request.pagination_key = list_response.pagination_key

        return item_count
    
    async def general_fetch_item(self, id: str) -> UntypedFetchResponse:
        """
        Fetches a general item from the registry.

        Parameters
        ----------
        id : str
            The ID of the item to fetch.

        Returns
        -------
        UntypedFetchResponse
            The fetch response containing the item details.
        """

        return await self._registry_client.general.general_fetch_item(
            id=id
        )

    
    async def get_current_provena_version(self) -> VersionResponse:
        """
        Gets the current Provena version deployed on your domain.

        Returns
        -------
        VersionResponse
            The response containing the current Provena version.
        """

        return await self._registry_client.general.get_current_provena_version()