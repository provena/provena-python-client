'''
Created Date: Thursday June 6th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday June 6th 2024 1:39:55 pm +1000
Modified By: Peter Baker
-----
Description: Datastore L2 Client.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients.client_helpers import *
from enum import Enum
from ProvenaInterfaces.DataStoreAPI import *
from provenaclient.models import HealthCheckResponse, RevertMetadata
from ProvenaInterfaces.RegistryModels import CollectionFormat
from ProvenaInterfaces.RegistryAPI import NoFilterSubtypeListRequest, VersionRequest, VersionResponse, DatasetListResponse
from provenaclient.utils.helpers import *


class DatastoreEndpoints(str, Enum):
    """An ENUM containing the datastore-api endpoints."""

    # Completed.
    GET_REGISTRY_ITEMS_FETCH_DATASET = "/registry/items/fetch-dataset"
    POST_REGISTER_MINT_DATASET = "/register/mint-dataset"
    GET_HEALTH_CHECK = "/"
    POST_METADATA_VALIDATE_METADATA = "/metadata/validate-metadata"
    GET_METADATA_DATASET_SCHEMA = "/metadata/dataset-schema"
    POST_REGISTER_UPDATE_METADATA = "/register/update-metadata"
    PUT_REGISTER_REVERT_METADATA = "/register/revert-metadata"
    POST_REGISTER_VERSION = "/register/version"
    POST_REGISTRY_ITEMS_LIST = "/registry/items/list"
    POST_REGISTRY_ITEMS_GENERATE_PRESIGNED_URL = "/registry/items/generate-presigned-url"
    POST_REGISTRY_CREDENTIALS_GENERATE_READ_ACCESS_CREDENTIALS = "/registry/credentials/generate-read-access-credentials"
    POST_REGISTRY_CREDENTIALS_GENERATE_WRITE_ACCESS_CREDENTIALS = "/registry/credentials/generate-write-access-credentials"
    DELETE_RELEASE_SYS_REVIEWERS_DELETE = "/release/sys-reviewers/delete"
    POST_RELEASE_SYS_REVIEWERS_ADD = "/release/sys-reviewers/add"
    GET_RELEASE_SYS_REVIEWERS_LIST = "/release/sys-reviewers/list"
    POST_RELEASE_APPROVAL_REQUEST = "/release/approval-request"
    PUT_RELEASE_ACTION_APPROVAL_REQUEST = "/release/action-approval-request"


    # Not completed.
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"


# L2 interface.

class DatasetReviewSubClient(ClientService):

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialise the Datastore system reviewer sub client with authentication and configuration.

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
        return self._config.auth_api_endpoint + endpoint.value
    
    
    async def delete_dataset_reviewer(self, reviewer_id: str) -> None:
        """Delete a reviewer existing within the datastore.

        Parameters
        ----------
        reviewer_id : str
            Id of an existing reviewer within the system.
        """

        await parsed_delete_request_non_return(
            client=self, 
            url=self._build_endpoint(DatastoreEndpoints.DELETE_RELEASE_SYS_REVIEWERS_DELETE),
            error_message="Failed to delete reviewer!", 
            params={"reviewer_id": reviewer_id},
        )
    
    async def add_dataset_reviewer(self, reviewer_id: str) -> None: 
        """Add a reviewer to the datastore.

        Parameters
        ----------
        reviewer_id : str
            Valid Id of a reviewer.
        """

        await parsed_post_request_none_return(
            client=self, 
            url=self._build_endpoint(DatastoreEndpoints.POST_RELEASE_SYS_REVIEWERS_ADD),
            error_message="Failed to add reviewer!", 
            params={},
            json_body={"reviewer_id": reviewer_id},
        )
    
    """

    #TODO: This has to be completed, once a new pydantic defined response model is setup
    for this endpoint.

    async def list_reviewers(self) -> EmptyResponse: 

        return await parsed_post_request(
            client=self, 
            url=self._build_endpoint(DatastoreEndpoints.POST_RELEASE_SYS_REVIEWERS_ADD),
            error_message="Failed to add reviewer!", 
            params={},
            json_body={"reviewer_id": reviewer_id},
            model=EmptyResponse
        )

    """

    async def approval_request(self, approval_request_payload: ReleaseApprovalRequest) -> ReleaseApprovalRequestResponse:
        """Submit a request for approval of dataset through the datastore.

        Parameters
        ----------
        approval_request_payload : ReleaseApprovalRequest
            An object that requires the dataset id, approver id and notes

        Returns
        -------
        ReleaseApprovalRequestResponse
            Contains details of the approval request.
        """

        return await parsed_post_request(
            client=self, 
            url=self._build_endpoint(DatastoreEndpoints.POST_RELEASE_APPROVAL_REQUEST),
            error_message="Failed to create an approval request!", 
            params={},
            json_body=py_to_dict(approval_request_payload),
            model=ReleaseApprovalRequestResponse
        )
        
    async def action_approval_request(self, action_approval_request_payload: ActionApprovalRequest) -> ActionApprovalRequestResponse:
        """Action an approval request from a dataset approval request via the datastore.

        Parameters
        ----------
        action_approval_request : ActionApprovalRequest
            The dataset id, your decision of approval and any extra information 
            you want to add (notes).

        Returns
        -------
        ActionApprovalRequestResponse
            The details of the approval action and the relevant dataset details.
        """
        
        return await parsed_put_request(
            client=self, 
            url=self._build_endpoint(DatastoreEndpoints.PUT_RELEASE_ACTION_APPROVAL_REQUEST),
            error_message="Failed to action approval request!", 
            params={},
            json_body=py_to_dict(action_approval_request_payload),
            model=ActionApprovalRequestResponse
        )
    
    # Admin endpoint. 
    # TODO - This has to be done.
    #  async def generate_config_file(self) -> None: 
    #    pass


class DatastoreClient(ClientService):

    review: DatasetReviewSubClient

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialise the DatastoreClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

        self.review = DatasetReviewSubClient(auth = auth, config = config)

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
        
    async def validate_metadata(self, metadata_payload: CollectionFormat) -> StatusResponse:
        """Validates provided dataset info with the datastore API.

        Parameters
        ----------
        metadata_payload : CollectionFormat
            A structured format containing all necessary information to register a new dataset, including associations, 
            approvals, and dataset-specific information.


        Returns
        -------
        StatusResponse
            Response indicating whether your dataset metadata setup is valid and correct.
        """

        return await parsed_post_request_with_status(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_METADATA_VALIDATE_METADATA), 
            error_message="Dataset metadata validation failed!", 
            params = {},
            json_body=py_to_dict(metadata_payload),
            model = StatusResponse
        ) 
    
    async def update_metadata(self, handle_id: str, reason: str, metadata_payload: CollectionFormat) -> UpdateMetadataResponse:

        """Updates existing dataset metadata through datastore API.

        Returns
        -------
        UpdateMetadataResponse
            The updated metadata response from datastore.
        """

        return await parsed_post_request_with_status(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTER_UPDATE_METADATA),
            error_message="Dataset metadata update failed!", 
            params = {"handle_id": handle_id, "reason": reason}, 
            json_body=py_to_dict(metadata_payload), 
            model = UpdateMetadataResponse
        )
    
    async def revert_metadata(self, metadata_payload:RevertMetadata) -> StatusResponse:
        """Reverts the metadata for a dataset to a previous identified historical version.

        Parameters
        ----------
        metadata_payload : RevertMetadata
            The revert request, passed through to the registry API and requires
            dataset id, history id and reason for reverting.

        Returns
        -------
        StatusResponse
            Response indicating whether your dataset metadata setup is valid and correct.
        """

        return await parsed_put_request_with_status(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.PUT_REGISTER_REVERT_METADATA),
            error_message= "Dataset revert metadata failed!",
            params={},
            json_body= py_to_dict(metadata_payload),
            model=StatusResponse
        )
    
    async def version_dataset(self, version_dataset_payload: VersionRequest) -> VersionResponse:
        """Creates a new versioning of an existing dataset within Provena 
           through the Datastore.

        Parameters
        ----------
        version_dataset_payload : VersionRequest
            The request which includes the item ID and reason for versioning.

        Returns
        -------
        VersionResponse
            Response of the versioning of the dataset, containing new version ID and 
            job session ID.
        """

        return await parsed_post_request(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTER_VERSION),
            error_message= "Dataset versioning failed!",
            params={},
            json_body= py_to_dict(version_dataset_payload),
            model=VersionResponse
        )
    
    async def list_datasets(self, list_request: NoFilterSubtypeListRequest) -> DatasetListResponse:
        """Gets datasets within the datastore in a paginated fashion.

        Parameters
        ----------
        list_request : NoFilterSubtypeListRequest
            Contains parameters for the specified sorting criteria, 
            optional pagination key and amount of records
            to fetch.

        Returns
        -------
        ListRegistryResponse
            Response of fetching datasets from datastore API.
        """

        return await parsed_post_request_with_status(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTRY_ITEMS_LIST),
            error_message="List fetching failed",
            params = {},
            json_body=py_to_dict(list_request),
            model = DatasetListResponse
        )
    

    async def generate_presigned_url(self, presigned_url: PresignedURLRequest) -> PresignedURLResponse: 
        """Generates a presigned url for an existing dataset within the datastore.

        Parameters
        ----------
        presigned_url : PresignedURLRequest
            Contains the dataset id + file path + length of expiry of URL.

        Returns
        -------
        PresignedURLResponse
            A response containing the presigned url.
        """

        return await parsed_post_request(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTRY_ITEMS_GENERATE_PRESIGNED_URL), 
            error_message= "Dataset presigned url generation failed!",
            params={},
            json_body=py_to_dict(presigned_url),
            model=PresignedURLResponse
        )

    async def generate_read_access_credentials(self, read_access_credentials: CredentialsRequest) -> CredentialResponse:
        """Creates a read-access for a certain subdirectory of the S3 bucket.

        Parameters
        ----------
        read_access_credentials : CredentialsRequest
            Contains the dataset id + console session URL required flag (boolean)

        Returns
        -------
        CredentialResponse
            The AWS credentials creating read level access into the subset of the bucket requested in the S3 location object.
        """

        return await parsed_post_request(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTRY_CREDENTIALS_GENERATE_READ_ACCESS_CREDENTIALS), 
            error_message= "Read access credential creation failed!",
            params={},
            json_body=py_to_dict(read_access_credentials),
            model=CredentialResponse
        )
    
    async def generate_write_access_credentials(self, write_access_credentials: CredentialsRequest) -> CredentialResponse:
        """Creates a write-access for a certain subdirectory of the S3 bucket. 

        Parameters
        ----------
        write_access_credentials : CredentialsRequest
            Contains the dataset id + console session URL required flag (boolean)

        Returns
        -------
        CredentialResponse
            The AWS credentials creating write level access into the subset of the bucket requested in the S3 location object.
        """

        return await parsed_post_request(
            client = self, 
            url = self._build_endpoint(DatastoreEndpoints.POST_REGISTRY_CREDENTIALS_GENERATE_WRITE_ACCESS_CREDENTIALS), 
            error_message= "Write access credential creation failed!",
            params={},
            json_body=py_to_dict(write_access_credentials),
            model=CredentialResponse
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
    
    

    

    



