'''
Created Date: Thursday June 6th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday June 6th 2024 1:39:55 pm +1000
Modified By: Peter Baker
-----
Description: Incomplete Registry API L2 Client.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

28-06-2024 | Parth Kulkarni | Completion of L2 Interface of Registry with General, Admin and Other endpoints. 
18-06-2024 | Peter Baker | Initial structure setup to help dispatch into the various sub types in the L3.
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.models.general import HealthCheckResponse
from provenaclient.utils.config import Config
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from provenaclient.utils.registry_endpoints import *
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *


class GenericRegistryEndpoints(str, Enum):
    GET_HEALTH_CHECK = "/"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    GET_REGISTRY_GENERAL_ABOUT_VERSION = "/registry/general/about/version"
    GET_REGISTRY_GENERAL_FETCH = "/registry/general/fetch"
    POST_REGISTRY_GENERAL_LIST = "/registry/general/list"


class RegistryAdminEndpoints(str, Enum):
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_EXPORT = "/admin/export"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    POST_ADMIN_IMPORT = "/admin/import"
    POST_ADMIN_RESTORE_FROM_TABLE = "/admin/restore_from_table"

class RegistryAdminClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the RegistryAdminClient with authentication and configuration.

        Parameters
        ----------
        auth: AuthManager
            An abstract interface containing the user's requested auth flow method.
        config: Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: RegistryAdminEndpoints) -> str:
        return f"{self._config.registry_api_endpoint}{endpoint.value}"
    
    def _build_subtype_endpoint(self, action: RegistryAction, item_subtype: ItemSubType) -> str:
        return subtype_action_to_endpoint(
            base=self._config.registry_api_endpoint,
            action=action,
            item_subtype=item_subtype
        )

    async def export_items(self) -> RegistryExportResponse:
        """
        Exports all items from the registry.

        Returns
        -------
        RegistryExportResponse
            The response containing the exported items.
        """
        endpoint = self._build_endpoint(RegistryAdminEndpoints.GET_ADMIN_EXPORT)

        return await parsed_get_request_with_status(
            client=self,
            url=endpoint,
            params=None,
            error_message="Failed to export all items from the registry!",
            model=RegistryExportResponse
        )
    
    async def import_items(self, registry_import_request: RegistryImportRequest) -> RegistryImportResponse:
        """
        Imports items into the registry.

        Parameters
        ----------
        registry_import_request : RegistryImportRequest
            The import request containing the items to import.

        Returns
        -------
        RegistryImportResponse
            The response containing the result of the import operation.
        """
        endpoint = self._build_endpoint(RegistryAdminEndpoints.POST_ADMIN_IMPORT)

        return await parsed_post_request_with_status(
            client=self,
            url=endpoint,
            params=None,
            json_body=py_to_dict(registry_import_request),
            error_message="Failed to import items into the registry!",
            model=RegistryImportResponse
        )
    
    async def restore_items_from_dynamo_table(self, restore_request: RegistryRestoreRequest) -> RegistryImportResponse:
        """
        Restores items from a DynamoDB table into the registry.

        Parameters
        ----------
        restore_request : RegistryRestoreRequest
            The restore request containing the details for restoration.

        Returns
        -------
        RegistryImportResponse
            The response containing the result of the restore operation.
        """
        endpoint = self._build_endpoint(RegistryAdminEndpoints.POST_ADMIN_RESTORE_FROM_TABLE)

        return await parsed_post_request_with_status(
            client=self,
            url=endpoint,
            params=None,
            json_body=py_to_dict(restore_request),
            error_message="Failed to restore items from DynamoDB table into the registry!",
            model=RegistryImportResponse
        )
    
    async def generate_config_file(self, required_only: bool) -> str:
        """
        Generates a nicely formatted .env file of the current required/non-supplied properties.

        Used to quickly bootstrap a local environment or to understand currently deployed API.

        Parameters
        ----------
        required_only : bool
            Whether to include only required properties. By default True.

        Returns
        -------
        str
            The generated .env file content.
        """
        response = await validated_get_request(
            client=self,
            url=self._build_endpoint(RegistryAdminEndpoints.GET_ADMIN_CONFIG),
            error_message="Failed to generate config file",
            params={"required_only": required_only},
        )

        return response.text
    
    async def delete_item(self, id: str, item_subtype: ItemSubType) -> StatusResponse:
        """
        Deletes an item from the registry.

        Parameters
        ----------
        id : str
            The ID of the item to delete.
        item_subtype : ItemSubType
            The subtype of the item to delete.

        Returns
        -------
        StatusResponse
            The status response indicating the result of the deletion.
        """
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.DELETE, item_subtype=item_subtype
        )

        return await parsed_delete_request_with_status(
            client=self,
            params={'id': id},
            error_message=f"Failed to delete item with id {id} and subtype {item_subtype}",
            model=StatusResponse,
            url=endpoint
        )
    
class RegistryGeneralClient(ClientService):

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the RegistryGeneralClient with authentication and configuration.

        Parameters
        ----------
        auth: AuthManager
            An abstract interface containing the user's requested auth flow method.
        config: Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_subtype_endpoint(self, action: RegistryAction, item_subtype: ItemSubType) -> str:
        return subtype_action_to_endpoint(
            base=self._config.registry_api_endpoint,
            action=action,
            item_subtype=item_subtype
        )

    def _build_general_endpoint(self, endpoint: GenericRegistryEndpoints) -> str:
        return f"{self._config.registry_api_endpoint}{endpoint.value}"
    
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
        endpoint = self._build_general_endpoint(endpoint=GenericRegistryEndpoints.POST_REGISTRY_GENERAL_LIST)

        return await parsed_post_request_with_status(
            client=self,
            url=endpoint,
            params=None,
            json_body=py_to_dict(general_list_request),
            error_message=f"General list fetch failed!",
            model=PaginatedListResponse
        )
    
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
        endpoint = self._build_general_endpoint(endpoint=GenericRegistryEndpoints.GET_REGISTRY_GENERAL_FETCH)

        return await parsed_get_request_with_status(
            client=self,
            url=endpoint,
            params={"id": id},
            error_message=f"Failed to fetch item with id {id} from general registry!",
            model=UntypedFetchResponse
        )
    
    async def get_current_provena_version(self) -> VersionResponse:
        """
        Gets the current Provena version.

        Returns
        -------
        VersionResponse
            The response containing the current Provena version.
        """
        endpoint = self._build_general_endpoint(endpoint=GenericRegistryEndpoints.GET_REGISTRY_GENERAL_ABOUT_VERSION)

        return await parsed_get_request(
            client=self,
            url=endpoint,
            params=None,
            error_message="Failed to fetch the current Provena version of your instance.",
            model=VersionResponse
        )

class RegistryClient(ClientService):
    # Sub clients
    admin: RegistryAdminClient
    general: RegistryGeneralClient

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the RegistryClient with authentication and configuration.

        Parameters
        ----------
        auth: AuthManager
            An abstract interface containing the user's requested auth flow method.
        config: Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

        # Sub clients
        self.admin = RegistryAdminClient(auth=auth, config=config)
        self.general = RegistryGeneralClient(auth=auth, config=config)

    # Function to get the endpoint URL
    def _build_subtype_endpoint(self, action: RegistryAction, item_subtype: ItemSubType) -> str:
        return subtype_action_to_endpoint(
            base=self._config.registry_api_endpoint,
            action=action,
            item_subtype=item_subtype
        )

    def _build_general_endpoint(self, endpoint: GenericRegistryEndpoints) -> str:
        return f"{self._config.registry_api_endpoint}{endpoint.value}"

    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns
        -------
        HealthCheckResponse
            Response
        """
        return await parsed_get_request(
            client=self,
            url=self._build_general_endpoint(GenericRegistryEndpoints.GET_HEALTH_CHECK),
            error_message="Health check failed!",
            params={},
            model=HealthCheckResponse
        )

    async def fetch_item(self, id: str, item_subtype: ItemSubType, fetch_response_model: Type[BaseModelType], seed_allowed: Optional[bool] = None) -> BaseModelType:
        """
        Ascertains the correct endpoint based on the subtype provided, then runs the fetch operation, parsing the data as the specified model.

        Parameters
        ----------
        id : str
            The id of the item to fetch.
        item_subtype : ItemSubType
            The subtype of the item to fetch.
        fetch_response_model : Type[BaseModelType]
            The response pydantic model to parse as e.g. OrganisationFetchResponse
        seed_allowed : Optional[bool], optional
            Should the endpoint throw an error if the item is a seed item?  Defaults to None.

        Returns
        -------
        BaseModelType
            The fetch response parsed as the specified model.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.FETCH, item_subtype=item_subtype)

        # fetch the item from the subtype specific endpoint
        return await parsed_get_request_with_status(
            client=self,
            params={'id': id, 'seed_allowed': seed_allowed},
            error_message=f"Failed to fetch item with id {id} and subtype {item_subtype}.",
            model=fetch_response_model,
            url=endpoint,
        )

    async def update_item(self, id: str, reason: Optional[str], item_subtype: ItemSubType, domain_info: DomainInfoBase, update_response_model: Type[BaseModelType]) -> BaseModelType:
        """
        Ascertains the correct endpoint then runs the update operation on an existing item by providing new domain info.

        Parameters
        ----------
        id : str
            The id of item to update.
        reason : Optional[str]
            The reason for updating, if any
        item_subtype : ItemSubType
            The subtype to update
        domain_info : DomainInfoBase
            The domain info to replace existing item with
        update_response_model : Type[BaseModelType]
            The response model to parse e.g. StatusResponse

        Returns
        -------
        BaseModelType
            The response model parsed
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.UPDATE, item_subtype=item_subtype)

        # fetch the item from the subtype specific endpoint
        return await parsed_put_request_with_status(
            client=self,
            params={'id': id, 'reason': reason},
            json_body=py_to_dict(domain_info),
            error_message=f"Failed to update item with id {id} and subtype {item_subtype}.",
            model=update_response_model,
            url=endpoint,
        )

    async def list_items(self, list_items_payload: GeneralListRequest, item_subtype: ItemSubType, update_model_response: Type[BaseModelType]) -> BaseModelType:
        """
        Lists items within the registry based on filter criteria.

        Parameters
        ----------
        list_items_payload : GeneralListRequest
            The request containing filter and sort criteria.
        item_subtype : ItemSubType
            The subtype of the items to list.
        update_model_response : Type[BaseModelType]
            The response model to parse.

        Returns
        -------
        BaseModelType
            The response containing the list of items.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.LIST, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_post_request_with_status(
            client=self,
            params=None,
            json_body=py_to_dict(list_items_payload),
            error_message=f"Failed to list items for {item_subtype}",
            model=update_model_response,
            url=endpoint
        )

    async def seed_item(self, item_subtype: ItemSubType, seed_model_response: Type[BaseModelType]) -> BaseModelType:
        """
        Seeds an item in the registry.

        Parameters
        ----------
        item_subtype : ItemSubType
            The subtype of the item to seed.
        seed_model_response : Type[BaseModelType]
            The response model to parse.

        Returns
        -------
        BaseModelType
            The response containing the details of the seeded item.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.SEED, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_post_request_with_status(
            client=self,
            params=None,
            json_body=None,
            error_message=f"Failed to seed items for {item_subtype}",
            model=seed_model_response,
            url=endpoint
        )

    async def revert_item(self, revert_request: ItemRevertRequest, item_subtype: ItemSubType) -> ItemRevertResponse:
        """
        Reverts an item in the registry.

        Parameters
        ----------
        revert_request : ItemRevertRequest
            The revert request.
        item_subtype : ItemSubType
            The subtype of the item to revert.

        Returns
        -------
        ItemRevertResponse
            The revert response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.REVERT, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_put_request_with_status(
            client=self,
            params=None,
            json_body=py_to_dict(revert_request),
            error_message=f"Failed to revert items for {item_subtype}",
            model=ItemRevertResponse,
            url=endpoint
        )

    async def create_item(self, create_item_request: DomainInfoBase, item_subtype: ItemSubType, create_response_model: Type[BaseModelType]) -> BaseModelType:
        """
        Creates an item in the registry.

        Parameters
        ----------
        create_item_request : DomainInfoBase
            The domain information required to create the item.
        item_subtype : ItemSubType
            The subtype of the item to create.
        create_response_model : Type[BaseModelType]
            The response model to parse.

        Returns
        -------
        BaseModelType
            The response containing the details of the created item.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.CREATE, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_post_request_with_status(
            client=self,
            params=None,
            json_body=py_to_dict(create_item_request),
            error_message=f"Failed to create items for {item_subtype}",
            model=create_response_model,
            url=endpoint
        )

    async def get_schema(self, item_subtype: ItemSubType) -> JsonSchemaResponse:
        """
        Gets the schema for the item subtype.

        Parameters
        ----------
        item_subtype : ItemSubType
            The subtype of the item to get the schema for.

        Returns
        -------
        JsonSchemaResponse
            The JSON schema response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.SCHEMA, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_get_request_with_status(
            client=self,
            params=None,
            error_message=f"Failed to get schema for {item_subtype}",
            model=JsonSchemaResponse,
            url=endpoint
        )

    async def validate_item(self, validate_request: DomainInfoBase, item_subtype: ItemSubType) -> StatusResponse:
        """
        Validates an item in the registry.

        Parameters
        ----------
        validate_request : DomainInfoBase
            The domain information of the item to be validated.
        item_subtype : ItemSubType
            The subtype of the item to validate.

        Returns
        -------
        StatusResponse
            The status response indicating the result of the validation.
        """

        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.VALIDATE, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_post_request_with_status(
            client=self,
            params=None,
            json_body=py_to_dict(validate_request),
            error_message=f"Failed to validate item for {item_subtype}",
            model=StatusResponse,
            url=endpoint
        )

    async def evaluate_auth_access(self, id: str, item_subtype: ItemSubType) -> DescribeAccessResponse:
        """
        Evaluates the auth access for an item.

        Parameters
        ----------
        id : str
            The ID of the item to evaluate auth access for.
        item_subtype : ItemSubType
            The subtype of the item to evaluate auth access for.

        Returns
        -------
        DescribeAccessResponse
            The describe access response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.AUTH_EVALUATE, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_get_request(
            client=self,
            params={"id": id},
            error_message=f"Failed to evaluate auth access for {item_subtype}",
            model=DescribeAccessResponse,
            url=endpoint
        )

    async def get_auth_configuration(self, id: str, item_subtype: ItemSubType) -> AccessSettings:
        """
        Gets the auth configuration for an item.

        Parameters
        ----------
        id : str
            The ID of the item to get auth configuration for.
        item_subtype : ItemSubType
            The subtype of the item to get auth configuration for.

        Returns
        -------
        AccessSettings
            The access settings.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.AUTH_CONFIGURATION, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_get_request(
            client=self,
            params={"id": id},
            error_message=f"Failed to get auth config for {item_subtype}",
            model=AccessSettings,
            url=endpoint
        )

    async def modify_auth_configuration(self, id: str, auth_change_request: AccessSettings, item_subtype: ItemSubType) -> StatusResponse:
        """
        Modifies the auth configuration for an item.

        Parameters
        ----------
        id : str
            The ID of the item to modify auth configuration for.
        auth_change_request : AccessSettings
            The auth change request.
        item_subtype : ItemSubType
            The subtype of the item to modify auth configuration for.

        Returns
        -------
        StatusResponse
            The status response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.AUTH_CONFIGURATION, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_put_request_with_status(
            client=self,
            params={"id": id},
            json_body=py_to_dict(auth_change_request),
            error_message=f"Failed to modify auth config for {item_subtype}",
            model=StatusResponse,
            url=endpoint
        )

    async def get_auth_roles(self, item_subtype: ItemSubType) -> AuthRolesResponse:
        """
        Gets the auth roles for the item subtype.

        Parameters
        ----------
        item_subtype : ItemSubType
            The subtype of the item to get auth roles for.

        Returns
        -------
        AuthRolesResponse
            The auth roles response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.AUTH_ROLES, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_get_request(
            client=self,
            params=None,
            error_message=f"Failed to get auth roles for {item_subtype}",
            model=AuthRolesResponse,
            url=endpoint
        )

    async def lock_resource(self, lock_resource_request: LockChangeRequest, item_subtype: ItemSubType) -> StatusResponse:
        """
        Locks a resource in the registry.

        Parameters
        ----------
        lock_resource_request : LockChangeRequest
            The lock resource request.
        item_subtype : ItemSubType
            The subtype of the resource to lock.

        Returns
        -------
        StatusResponse
            The status response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.LOCK, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_put_request_with_status(
            client=self,
            params=None,
            json_body=py_to_dict(lock_resource_request),
            error_message=f"Failed to lock resource for {item_subtype}",
            model=StatusResponse,
            url=endpoint
        )

    async def unlock_resource(self, unlock_resource_request: LockChangeRequest, item_subtype: ItemSubType) -> StatusResponse:
        """
        Unlocks a resource in the registry.

        Parameters
        ----------
        unlock_resource_request : LockChangeRequest
            The unlock resource request.
        item_subtype : ItemSubType
            The subtype of the resource to unlock.

        Returns
        -------
        StatusResponse
            The status response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.UNLOCK, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_put_request_with_status(
            client=self,
            params=None,
            json_body=py_to_dict(unlock_resource_request),
            error_message=f"Failed to unlock resource for {item_subtype}",
            model=StatusResponse,
            url=endpoint
        )

    async def get_lock_history(self, handle_id: str, item_subtype: ItemSubType) -> LockHistoryResponse:
        """
        Gets the lock history for an item.

        Parameters
        ----------
        handle_id : str
            The handle ID of the item to get lock history for.
        item_subtype : ItemSubType
            The subtype of the item to get lock history for.

        Returns
        -------
        LockHistoryResponse
            The lock history response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.LOCK_HISTORY, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_get_request_with_status(
            client=self,
            params={"id": handle_id},
            error_message=f"Failed to get lock history for id {handle_id} for subtype {item_subtype}",
            model=LockHistoryResponse,
            url=endpoint
        )

    async def get_lock_status(self, id: str, item_subtype: ItemSubType) -> LockStatusResponse:
        """
        Gets the lock status for an item.

        Parameters
        ----------
        id : str
            The item ID.
        item_subtype : ItemSubType
            The subtype of the item to get lock status for.

        Returns
        -------
        LockStatusResponse
            The lock status response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.LOCK_HISTORY, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_get_request_with_status(
            client=self,
            params={"id": id},
            error_message=f"Failed to get lock status for id {id} with subtype {item_subtype}",
            model=LockStatusResponse,
            url=endpoint
        )

    async def version(self, version_request: VersionRequest, item_subtype: ItemSubType) -> VersionResponse:
        """
        Versions an item in the registry.

        Parameters
        ----------
        version_request : VersionRequest
            The version request containing the version details.
        item_subtype : ItemSubType
            The subtype of the item to version.

        Returns
        -------
        VersionResponse
            The version response.
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.VERSION, item_subtype=item_subtype
        )

        # fetch item from the subtype specific endpoint
        return await parsed_post_request(
            client=self,
            params=None,
            json_body=py_to_dict(version_request),
            error_message=f"Failed to complete versioning for subtype {item_subtype}",
            model=VersionResponse,
            url=endpoint
        )