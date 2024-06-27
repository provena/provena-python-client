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
from provenaclient.utils.helpers import read_file_helper, write_file_helper, get_and_validate_file_path



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

        return await self._registry_client.admin.export_items()
    
    async def import_items(self, registry_import_request: RegistryImportRequest) -> RegistryImportResponse:

        return await self._registry_client.admin.import_items(
            registry_import_request=registry_import_request
        )
    
    async def restore_items_from_dynamo_table(self, restore_request: RegistryRestoreRequest) -> RegistryImportResponse:

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
    
    async def list_items(self, list_items_payload: GeneralListRequest) -> OrganisationListResponse:
        """Lists all orgainsations within registry based on filter
        criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            Payload contaning the filter/sort criteria
        """

        return await self._registry_client.list_items(
            list_items_payload=list_items_payload,
            item_subtype=ItemSubType.ORGANISATION, 
            update_model_response=OrganisationListResponse
        )
    
    async def seed_item(self) -> OrganisationSeedResponse:

        return await self._registry_client.seed_item(
            item_subtype=ItemSubType.ORGANISATION,
            update_model_response=OrganisationSeedResponse
        )
    
    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:

        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def create_item(self, create_item_request: OrganisationDomainInfo) -> OrganisationCreateResponse:

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=ItemSubType.ORGANISATION,
            update_model_response=OrganisationCreateResponse
        )
    
    async def get_schema(self) -> JsonSchemaResponse:

        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def validate_item(self, validate_request: OrganisationDomainInfo) -> StatusResponse:

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def evaluate_auth_access(self, id:str) -> DescribeAccessResponse:

        return await self._registry_client.evaluate_auth_access(
            id=id, 
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def get_auth_configuration(self, id:str) -> AccessSettings:

        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:

        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def get_auth_roles(self) -> AuthRolesResponse:

        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.ORGANISATION
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def get_lock_history(self, id: str) -> LockHistoryResponse:

        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.ORGANISATION
        )
    
    async def get_lock_status(self, id: str) -> LockStatusResponse:

        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.ORGANISATION
        )
    


class PersonClient(ModuleService):
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

    async def fetch(self, id: str, seed_allowed: Optional[bool] = None) -> PersonFetchResponse:
        """
        Fetches a person from the registry

        Args:
            id (str): The person ID
            seed_allowed (Optional[bool], optional): Allow seed items. Defaults to None.

        Returns:
            OrganisationFetchResponse: The fetch response
        """
        return await self._registry_client.fetch_item(
            id=id,
            item_subtype=ItemSubType.PERSON,
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
            item_subtype=ItemSubType.PERSON,
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
            item_subtype=ItemSubType.PERSON, 
            update_model_response=PersonListResponse
        )
    
    async def seed_item(self) -> PersonSeedResponse:

        return await self._registry_client.seed_item(
            item_subtype=ItemSubType.PERSON,
            update_model_response=PersonSeedResponse
        )
    
    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:

        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=ItemSubType.PERSON
        )
    
    async def create_item(self, create_item_request: PersonDomainInfo) -> PersonCreateResponse:

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=ItemSubType.PERSON,
            update_model_response=PersonCreateResponse
        )
    
    async def get_schema(self) -> JsonSchemaResponse:

        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.PERSON
        )
    
    async def validate_item(self, validate_request: PersonDomainInfo) -> StatusResponse:

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=ItemSubType.PERSON
        )
    
    async def evaluate_auth_access(self, id:str) -> DescribeAccessResponse:

        return await self._registry_client.evaluate_auth_access(
            id=id, 
            item_subtype=ItemSubType.PERSON
        )
    
    async def get_auth_configuration(self, id:str) -> AccessSettings:

        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.PERSON
        )
    
    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:

        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.PERSON
        )
    
    async def get_auth_roles(self) -> AuthRolesResponse:

        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.PERSON
        )
    
    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.PERSON
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.PERSON
        )
    
    async def get_lock_history(self, id: str) -> LockHistoryResponse:

        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.PERSON
        )
    
    async def get_lock_status(self, id: str) -> LockStatusResponse:

        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.PERSON
        )

class CreateActivityClient(ModuleService):
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
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the registry scoped as private.
        self._registry_client = registry_client

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
            item_subtype=ItemSubType.CREATE,
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
            item_subtype=ItemSubType.CREATE,
            update_model_response=CreateListResponse
        )

    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for create activity items

        Returns
        -------
        JsonSchemaResponse: The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.CREATE
        )

    async def validate_item(self, validate_request: CreateDomainInfo) -> StatusResponse:
        """
        Validates a create activity item in the registry

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
            item_subtype=ItemSubType.CREATE
        )

    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for a create activity item

        Parameters
        ----------
        id : str
            The create activity item ID

        Returns
        -------
        DescribeAccessResponse: The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id,
            item_subtype=ItemSubType.CREATE
        )

    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for a create activity item

        Parameters
        ----------
        id : str
            The create activity item ID

        Returns
        -------
        AccessSettings: The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.CREATE
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for a create activity item

        Parameters
        ----------
        id : str
            The create activity item ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.CREATE
        )

    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for create activity items

        Returns
        -------
        AuthRolesResponse: The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.CREATE
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a create activity item in the registry

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.CREATE
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a create activity item in the registry

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.CREATE
        )

    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for a create activity item

        Parameters
        ----------
        id : str
            The create activity item ID

        Returns
        -------
        LockHistoryResponse: The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.CREATE
        )

    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for a create activity item

        Parameters
        ----------
        id : str
            The create activity item ID

        Returns
        -------
        LockStatusResponse: The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.CREATE
        )


class VersionActivityClient(ModuleService):
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
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the registry scoped as private.
        self._registry_client = registry_client

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
            item_subtype=ItemSubType.VERSION,
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
            item_subtype=ItemSubType.VERSION,
            update_model_response=VersionListResponse
        )

    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for version activity items

        Returns
        -------
        JsonSchemaResponse: The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.VERSION
        )

    async def validate_item(self, validate_request: VersionDomainInfo) -> StatusResponse:
        """
        Validates a version activity item in the registry

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
            item_subtype=ItemSubType.VERSION
        )

    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for a version activity item

        Parameters
        ----------
        id : str
            The version activity item ID

        Returns
        -------
        DescribeAccessResponse: The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id,
            item_subtype=ItemSubType.VERSION
        )

    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for a version activity item

        Parameters
        ----------
        id : str
            The version activity item ID

        Returns
        -------
        AccessSettings: The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.VERSION
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for a version activity item

        Parameters
        ----------
        id : str
            The version activity item ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.VERSION
        )

    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for version activity items

        Returns
        -------
        AuthRolesResponse: The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.VERSION
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a version activity item in the registry

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.VERSION
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a version activity item in the registry

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.VERSION
        )

    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for a version activity item

        Parameters
        ----------
        id : str
            The version activity item ID

        Returns
        -------
        LockHistoryResponse: The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.VERSION
        )

    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for a version activity item

        Parameters
        ----------
        id : str
            The version activity item ID

        Returns
        -------
        LockStatusResponse: The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.VERSION
        )


class ModelRunActivityClient(ModuleService):
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
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the registry scoped as private.
        self._registry_client = registry_client

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
            item_subtype=ItemSubType.MODEL_RUN,
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
            item_subtype=ItemSubType.MODEL_RUN,
            update_model_response=ModelRunListResponse
        )

    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for model run activity items

        Returns
        -------
        JsonSchemaResponse: The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def validate_item(self, validate_request: ModelRunDomainInfo) -> StatusResponse:
        """
        Validates a model run activity item in the registry

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
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for a model run activity item

        Parameters
        ----------
        id : str
            The model run activity item ID

        Returns
        -------
        DescribeAccessResponse: The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id,
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for a model run activity item

        Parameters
        ----------
        id : str
            The model run activity item ID

        Returns
        -------
        AccessSettings: The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for a model run activity item

        Parameters
        ----------
        id : str
            The model run activity item ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for model run activity items

        Returns
        -------
        AuthRolesResponse: The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a model run activity item in the registry

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a model run activity item in the registry

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for a model run activity item

        Parameters
        ----------
        id : str
            The model run activity item ID

        Returns
        -------
        LockHistoryResponse: The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.MODEL_RUN
        )

    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for a model run activity item

        Parameters
        ----------
        id : str
            The model run activity item ID

        Returns
        -------
        LockStatusResponse: The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.MODEL_RUN
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
            item_subtype=ItemSubType.MODEL, 
            update_model_response=ModelListResponse
        )
    
    async def seed_item(self) -> ModelSeedResponse:

        return await self._registry_client.seed_item(
            item_subtype=ItemSubType.MODEL,
            update_model_response=ModelSeedResponse
        )
    
    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:

        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=ItemSubType.MODEL
        )
    
    async def create_item(self, create_item_request: ModelDomainInfo) -> ModelCreateResponse:

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=ItemSubType.MODEL,
            update_model_response=ModelCreateResponse
        )
    
    async def get_schema(self) -> JsonSchemaResponse:

        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.MODEL
        )
    
    async def validate_item(self, validate_request: ModelDomainInfo) -> StatusResponse:

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=ItemSubType.MODEL
        )
    
    async def evaluate_auth_access(self, id:str) -> DescribeAccessResponse:

        return await self._registry_client.evaluate_auth_access(
            id=id, 
            item_subtype=ItemSubType.MODEL
        )
    
    async def get_auth_configuration(self, id:str) -> AccessSettings:

        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.MODEL
        )
    
    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:

        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.MODEL
        )
    
    async def get_auth_roles(self) -> AuthRolesResponse:

        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.MODEL
        )
    
    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.MODEL
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.MODEL
        )
    
    async def get_lock_history(self, id: str) -> LockHistoryResponse:

        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.MODEL
        )
    
    async def get_lock_status(self, id: str) -> LockStatusResponse:

        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.MODEL
        )
    
    async def version_item(self, version_request: VersionRequest) -> VersionResponse:

        return await self._registry_client.version(
            version_request=version_request,
            item_subtype=ItemSubType.MODEL
        )
    
class ModelRunWorkFlowClient(ModuleService):
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
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
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
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
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
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
            update_model_response=ModelRunWorkflowTemplateListResponse
        )
    
    async def seed_item(self) -> ModelSeedResponse:

        return await self._registry_client.seed_item(
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
            update_model_response=ModelSeedResponse
        )
    
    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:

        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def create_item(self, create_item_request: ModelRunWorkflowTemplateDomainInfo) -> ModelRunWorkflowTemplateCreateResponse:

        return await self._registry_client.create_item(
            create_item_request=create_item_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
            update_model_response=ModelRunWorkflowTemplateCreateResponse
        )
    
    async def get_schema(self) -> JsonSchemaResponse:

        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def validate_item(self, validate_request: ModelRunWorkflowTemplateDomainInfo) -> StatusResponse:

        return await self._registry_client.validate_item(
            validate_request=validate_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def evaluate_auth_access(self, id:str) -> DescribeAccessResponse:

        return await self._registry_client.evaluate_auth_access(
            id=id, 
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def get_auth_configuration(self, id:str) -> AccessSettings:

        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:

        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def get_auth_roles(self) -> AuthRolesResponse:

        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:

        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def get_lock_history(self, id: str) -> LockHistoryResponse:

        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def get_lock_status(self, id: str) -> LockStatusResponse:

        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    
    async def version_item(self, version_request: VersionRequest) -> VersionResponse:

        return await self._registry_client.version(
            version_request=version_request,
            item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE
        )
    

class DatasetTemplateClient(ModuleService):
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
            item_subtype=ItemSubType.DATASET_TEMPLATE,
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
            item_subtype=ItemSubType.DATASET_TEMPLATE,
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
            item_subtype=ItemSubType.DATASET_TEMPLATE,
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
            item_subtype=ItemSubType.DATASET_TEMPLATE,
            update_model_response=DatasetTemplateSeedResponse
        )

    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:
        """
        Reverts a dataset template in the registry

        Parameters
        ----------
        revert_request : ItemRevertRequest
            The revert request

        Returns
        -------
        ItemRevertResponse: The revert response
        """
        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=ItemSubType.DATASET_TEMPLATE
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
            item_subtype=ItemSubType.DATASET_TEMPLATE,
            update_model_response=DatasetTemplateCreateResponse
        )

    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for dataset templates

        Returns
        -------
        JsonSchemaResponse: The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def validate_item(self, validate_request: DatasetTemplateDomainInfo) -> StatusResponse:
        """
        Validates a dataset template in the registry

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
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for a dataset template

        Parameters
        ----------
        id : str
            The dataset template ID

        Returns
        -------
        DescribeAccessResponse: The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id,
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for a dataset template

        Parameters
        ----------
        id : str
            The dataset template ID

        Returns
        -------
        AccessSettings: The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for a dataset template

        Parameters
        ----------
        id : str
            The dataset template ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for dataset templates

        Returns
        -------
        AuthRolesResponse: The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a dataset template in the registry

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a dataset template in the registry

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for a dataset template

        Parameters
        ----------
        id : str
            The dataset template ID

        Returns
        -------
        LockHistoryResponse: The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )

    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for a dataset template

        Parameters
        ----------
        id : str
            The dataset template ID

        Returns
        -------
        LockStatusResponse: The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.DATASET_TEMPLATE
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
            item_subtype=ItemSubType.DATASET_TEMPLATE
        )


class DatasetClient(ModuleService):
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
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the registry scoped as private.
        self._registry_client = registry_client

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
            item_subtype=ItemSubType.DATASET,
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
            item_subtype=ItemSubType.DATASET,
            update_model_response=DatasetListResponse
        )

    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for datasets

        Returns
        -------
        JsonSchemaResponse: The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.DATASET
        )

    async def validate_item(self, validate_request: DatasetDomainInfo) -> StatusResponse:
        """
        Validates a dataset in the registry

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
            item_subtype=ItemSubType.DATASET
        )

    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for a dataset

        Parameters
        ----------
        id : str
            The dataset ID

        Returns
        -------
        DescribeAccessResponse: The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id,
            item_subtype=ItemSubType.DATASET
        )

    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for a dataset

        Parameters
        ----------
        id : str
            The dataset ID

        Returns
        -------
        AccessSettings: The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.DATASET
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for a dataset

        Parameters
        ----------
        id : str
            The dataset ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.DATASET
        )

    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for datasets

        Returns
        -------
        AuthRolesResponse: The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.DATASET
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a dataset in the registry

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.DATASET
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a dataset in the registry

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.DATASET
        )

    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for a dataset

        Parameters
        ----------
        id : str
            The dataset ID

        Returns
        -------
        LockHistoryResponse: The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.DATASET
        )

    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for a dataset

        Parameters
        ----------
        id : str
            The dataset ID

        Returns
        -------
        LockStatusResponse: The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.DATASET
        )

class StudyClient(ModuleService):
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
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the registry scoped as private.
        self._registry_client = registry_client

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
            item_subtype=ItemSubType.STUDY,
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
            item_subtype=ItemSubType.STUDY,
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
            item_subtype=ItemSubType.STUDY,
            update_model_response=StudySeedResponse
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
            item_subtype=ItemSubType.STUDY,
            domain_info=domain_info,
            reason=reason,
            update_response_model=StatusResponse,
        )

    async def revert_item(self, revert_request: ItemRevertRequest) -> ItemRevertResponse:
        """
        Reverts a study in the registry

        Parameters
        ----------
        revert_request : ItemRevertRequest
            The revert request

        Returns
        -------
        ItemRevertResponse: The revert response
        """
        return await self._registry_client.revert_item(
            revert_request=revert_request,
            item_subtype=ItemSubType.STUDY
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
            item_subtype=ItemSubType.STUDY,
            update_model_response=StudyCreateResponse
        )

    async def get_schema(self) -> JsonSchemaResponse:
        """
        Gets the schema for studies

        Returns
        -------
        JsonSchemaResponse: The JSON schema response
        """
        return await self._registry_client.get_schema(
            item_subtype=ItemSubType.STUDY
        )

    async def validate_item(self, validate_request: StudyDomainInfo) -> StatusResponse:
        """
        Validates a study in the registry

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
            item_subtype=ItemSubType.STUDY
        )

    async def evaluate_auth_access(self, id: str) -> DescribeAccessResponse:
        """
        Evaluates the auth access for a study

        Parameters
        ----------
        id : str
            The study ID

        Returns
        -------
        DescribeAccessResponse: The describe access response
        """
        return await self._registry_client.evaluate_auth_access(
            id=id,
            item_subtype=ItemSubType.STUDY
        )

    async def get_auth_configuration(self, id: str) -> AccessSettings:
        """
        Gets the auth configuration for a study

        Parameters
        ----------
        id : str
            The study ID

        Returns
        -------
        AccessSettings: The access settings
        """
        return await self._registry_client.get_auth_configuration(
            id=id,
            item_subtype=ItemSubType.STUDY
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings) -> StatusResponse:
        """
        Modifies the auth configuration for a study

        Parameters
        ----------
        id : str
            The study ID
        auth_change_request : AccessSettings
            The auth change request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.modify_auth_configuration(
            id=id,
            auth_change_request=auth_change_request,
            item_subtype=ItemSubType.STUDY
        )

    async def get_auth_roles(self) -> AuthRolesResponse:
        """
        Gets the auth roles for studies

        Returns
        -------
        AuthRolesResponse: The auth roles response
        """
        return await self._registry_client.get_auth_roles(
            item_subtype=ItemSubType.STUDY
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Locks a study in the registry

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.lock_resource(
            lock_resource_request=lock_resource_request,
            item_subtype=ItemSubType.STUDY
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest) -> StatusResponse:
        """
        Unlocks a study in the registry

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request

        Returns
        -------
        StatusResponse: The status response
        """
        return await self._registry_client.unlock_resource(
            unlock_resource_request=unlock_resource_request,
            item_subtype=ItemSubType.STUDY
        )

    async def get_lock_history(self, id: str) -> LockHistoryResponse:
        """
        Gets the lock history for a study

        Parameters
        ----------
        id : str
            The study ID

        Returns
        -------
        LockHistoryResponse: The lock history response
        """
        return await self._registry_client.get_lock_history(
            handle_id=id,
            item_subtype=ItemSubType.STUDY
        )

    async def get_lock_status(self, id: str) -> LockStatusResponse:
        """
        Gets the lock status for a study

        Parameters
        ----------
        id : str
            The study ID

        Returns
        -------
        LockStatusResponse: The lock status response
        """
        return await self._registry_client.get_lock_status(
            id=id,
            item_subtype=ItemSubType.STUDY
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
    

    async def list_general_registry_items(self, general_list_request: GeneralListRequest) -> PaginatedListResponse:

        return await self._registry_client.general.list_general_registry_items(
            general_list_request=general_list_request
        )
    
    async def general_fetch_item(self, id: str) -> UntypedFetchResponse:

        return await self._registry_client.general.general_fetch_item(
            id=id
        )
    
    async def get_current_provena_version(self) -> VersionResponse:

        return await self._registry_client.general.get_current_provena_version()
