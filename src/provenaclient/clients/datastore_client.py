from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients.client_helpers import *
from enum import Enum
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse, UpdateMetadataResponse
from provenaclient.models import HealthCheckResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat
from provenaclient.utils.helpers import *




class DatastoreEndpoints(str, Enum):
    """An ENUM containing the datastore-api endpoints."""

    # Completed.
    GET_REGISTRY_ITEMS_FETCH_DATASET = "/registry/items/fetch-dataset"
    POST_REGISTER_MINT_DATASET = "/register/mint-dataset"
    GET_HEALTH_CHECK = "/"
    POST_METADATA_VALIDATE_METADATA = "/metadata/validate-metadata"


    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    GET_METADATA_DATASET_SCHEMA = "/metadata/dataset-schema"
    POST_REGISTER_UPDATE_METADATA = "/register/update-metadata"
    PUT_REGISTER_REVERT_METADATA = "/register/revert-metadata"
    POST_REGISTER_VERSION = "/register/version"
    POST_REGISTRY_ITEMS_LIST = "/registry/items/list"
    POST_REGISTRY_ITEMS_GENERATE_PRESIGNED_URL = "/registry/items/generate-presigned-url"
    POST_REGISTRY_CREDENTIALS_GENERATE_READ_ACCESS_CREDENTIALS = "/registry/credentials/generate-read-access-credentials"
    POST_REGISTRY_CREDENTIALS_GENERATE_WRITE_ACCESS_CREDENTIALS = "/registry/credentials/generate-write-access-credentials"
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    DELETE_RELEASE_SYS_REVIEWERS_DELETE = "/release/sys-reviewers/delete"
    POST_RELEASE_SYS_REVIEWERS_ADD = "/release/sys-reviewers/add"
    GET_RELEASE_SYS_REVIEWERS_LIST = "/release/sys-reviewers/list"
    POST_RELEASE_APPROVAL_REQUEST = "/release/approval-request"
    PUT_RELEASE_ACTION_APPROVAL_REQUEST = "/release/action-approval-request"


# L2 interface.


class DatastoreClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the DatastoreClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: DatastoreEndpoints) -> str:
        return self._config.datastore_api_endpoint + endpoint.value
        
    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(DatastoreEndpoints.GET_HEALTH_CHECK),
            error_message="Health check failed!",
            params={},
            model=HealthCheckResponse
        )
    
    # Focusing on Metadata
    
    async def validate_metadata(self, metadata_payload: CollectionFormat) -> StatusResponse:

        return await parsed_post_request_with_status(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_METADATA_VALIDATE_METADATA), 
            error_message="Dataset metadata validation failed!", 
            params = {},
            json_body=py_to_dict(metadata_payload),
            model = StatusResponse
        ) 
    
    async def update_metadata(self, metadata_payload: CollectionFormat) -> UpdateMetadataResponse:

        return await parsed_post_request_with_status(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTER_UPDATE_METADATA),
            error_message="Dataset metadata update failed!", 
            params = {}, 
            json_body=py_to_dict(metadata_payload), 
            model = UpdateMetadataResponse
        )
    

    async def fetch_dataset(self, id: str) -> RegistryFetchResponse:
        """Fetches a dataset from the datastore based on the provided
        ID.

        Parameters
        ----------
        id : str
            The unique identifier of the dataset to be retrieved.
            For example: "10378.1/1451860"

        Returns
        -------
        RegistryFetchResponse
            A interactive python datatype of type RegistryFetchResponse
            containing the dataset details.

        Raises
        ------
        CustomTimeoutException
            Raised if the request times out.
        Exception
            General exception for handling unexpected errors.
        ValueError
            Raised if there is an issue in parsing the response into the expected model.
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                DatastoreEndpoints.GET_REGISTRY_ITEMS_FETCH_DATASET),
            error_message=f"Failed to fetch dataset with id {id}...",
            params={"handle_id": id},
            model=RegistryFetchResponse
        )

    async def mint_dataset(self, dataset_info: CollectionFormat) -> MintResponse:
        """Creates a new dataset in the datastore with the provided dataset information.

        Parameters
        ----------
        dataset_info : CollectionFormat
            A structured format containing all necessary information to register a new dataset, including associations, 
            approvals, and dataset-specific information.

        Returns
        -------
        MintResponse
            A interactive python datatype of type MintResponse
            containing the newly created dataset details.

        Raises
        ------
        BadRequestException
            Raised if the server returns a 400 status code, indicating a bad request.
        CustomTimeoutException
            Raised if the request times out.
        Exception
            General exception for handling unexpected errors.
        ValueError
            Raised if there is an issue in parsing the response into the expected model.

        """
        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(DatastoreEndpoints.POST_REGISTER_MINT_DATASET),
            error_message="Failed to mint the desired dataset...",
            params={},
            json_body=py_to_dict(dataset_info),
            model=MintResponse
        )
