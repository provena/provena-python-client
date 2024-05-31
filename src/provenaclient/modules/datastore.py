from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import DatastoreClient, SearchClient
from ProvenaInterfaces.DataStoreAPI import *
from ProvenaInterfaces.RegistryModels import CollectionFormat, ItemSubType
from provenaclient.models import HealthCheckResponse, LoadedSearchResponse, LoadedSearchItem, UnauthorisedSearchItem, FailedSearchItem, VersionDatasetRequest, VersionDatasetResponse, RevertMetadata
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from ProvenaInterfaces.RegistryAPI import NoFilterSubtypeListRequest
from typing import AsyncGenerator, List

# L3 interface.

DEFAULT_SEARCH_LIMIT = 25



class DatastoreSubModule(ModuleService):
    _datastore_client: DatastoreClient

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient) -> None:
        """
        System reviewer/admin sub module of the Datastore API functionality

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
        self._datastore_client = datastore_client


    async def delete_dataset_reviewer(self, reviewer_id: str) -> None: 
        """Delete a reviewer.  

        Parameters
        ----------
        reviewer_id : str
            Id of an existing reviewer within the system.
        """
        await self._datastore_client.admin.delete_dataset_reviewer(reviewer_id=reviewer_id)

    async def add_dataset_reviewer(self, reviewer_id: str) -> None: 
        """Add a reviewer.

        Parameters
        ----------
        reviewer_id : str
            Id of a reviewer.

        """

        await self._datastore_client.admin.add_dataset_reviewer(reviewer_id=reviewer_id)

    """
    async def list_reviewers(self) -> TODO: 
        TODO

    I cannot find the exact type annotations of this method, and investigating the back-end code was not helpful either. 
    """

    async def dataset_approval_request(self, approval_request: ReleaseApprovalRequest) -> ReleaseApprovalRequestResponse:
        """Submit a request for approval of dataset.

        Parameters
        ----------
        approval_request : ReleaseApprovalRequest
            An object that requires the dataset id, approver id and notes

        Returns
        -------
        ReleaseApprovalRequestResponse:
            Contains details of the approval request.
            
        """

        return await self._datastore_client.admin.approval_request(approval_request_payload= approval_request)
    
    async def action_approval_request(self, action_approval_request: ActionApprovalRequest)-> ActionApprovalRequestResponse:
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

        return await self._datastore_client.admin.action_approval_request(action_approval_request_payload= action_approval_request) 



class Datastore(ModuleService):
    _datastore_client: DatastoreClient
    _search_client: SearchClient

    current_pagination_request: Optional[NoFilterSubtypeListRequest]
    previous_keys: List[Dict[str, Any]]

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient, search_client: SearchClient) -> None:
        """Initialises a new datastore object, which sits between the user and the datastore api operations.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance. 
        datastore_client : DatastoreClient
            This client interacts with the Datastore API's.
        """
        self._auth = auth
        self._config = config

        # Clients related to the datastore scoped as private.
        self._datastore_client = datastore_client
        self._search_client = search_client

        # Variables to hold information about current progress of pagination. 
        self.current_pagination_request: Optional[NoFilterSubtypeListRequest] = None
        self.previous_keys: List[Dict[str, Any]] = []

    async def get_health_check(self) -> HealthCheckResponse:
        """Health check the API

        Returns
        -------
        HealthCheckResponse
            Response
        """

        return await self._datastore_client.get_health_check()

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

        """

        return await self._datastore_client.fetch_dataset(id)

    async def mint_dataset(self, dataset_mint_info: CollectionFormat) -> MintResponse:
        """Creates a new dataset in the datastore with the provided dataset information.

        Parameters
        ----------
        dataset_mint_info : CollectionFormat
            A structured format containing all necessary information to register a new dataset, including associations, 
            approvals, and dataset-specific information.

        Returns
        -------
        MintResponse
            A interactive python datatype of type MintResponse
            containing the newly created dataset details.

        """

        return await self._datastore_client.mint_dataset(dataset_mint_info)
    
    async def validate_dataset_metadata(self, metadata_payload: CollectionFormat) -> StatusResponse:
        """Validates the dataset metadata creation for testing and does not publish.

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

        return await self._datastore_client.validate_metadata(metadata_payload=metadata_payload)
    
    async def update_dataset_metadata(self, handle_id: str, reason: str, metadata_payload: CollectionFormat) -> UpdateMetadataResponse:
        """Updates an existing dataset's metadata.

        Parameters
        ----------
        handle_id : str
            The id of the dataset.
        reason : str
            The reason for changing metadata of the dataset.
        metadata_payload : CollectionFormat
            A structured format containing all necessary information to register a new dataset, including associations, 
            approvals, and dataset-specific information.

        Returns
        -------
        UpdateMetadataResponse
            The updated metadata response
        """

        return await self._datastore_client.update_metadata(handle_id=handle_id, reason=reason, metadata_payload=metadata_payload)
    
    async def revert_dataset_metadata(self, metadata_payload: RevertMetadata) -> StatusResponse:
        """Reverts the metadata for a dataset to a previous identified historical version.

        Parameters
        ----------
        metadata_payload : RevertMetadata
            The revert request, passed through to the registry API and requires
            dataset id, history id and reason for reverting.

        Returns
        -------
        StatusResponse
            Response indicating whether your dataset revert metadata request was correct.
        """

        return await self._datastore_client.revert_metadata(metadata_payload=metadata_payload)
    
    async def version_dataset(self, version_request: VersionDatasetRequest) -> VersionDatasetResponse: 
        """Versioning operation which creates a new version from the specified ID.

        Parameters
        ----------
        version_request : VersionDatasetRequest
            The request which includes the item ID and reason for versioning.

        Returns
        -------
        VersionDatasetResponse
            Response of the versioning of the dataset, containing new version ID and 
            job session ID.
        """

        return await self._datastore_client.version_dataset(version_dataset_payload=version_request)
    
    async def list_all_datasets(self, list_dataset_request: NoFilterSubtypeListRequest) -> AsyncGenerator[ListRegistryResponse, None]:

        """I will treat limit and page size as the same thing here"""

        count = 0 
        self.current_pagination_request = list_dataset_request

        while count < list_dataset_request.page_size:
            dataset = await self._datastore_client.get_all_dataset(list_request= list_dataset_request)
            yield dataset

            if count >= list_dataset_request.page_size:
                break

            if not dataset.pagination_key:
                return
            
            count = count + 1

            self.previous_keys.append(dataset.pagination_key)
            self.current_pagination_request.pagination_key = dataset.pagination_key

    async def next_dataset(self, list_dataset_request: Optional[NoFilterSubtypeListRequest] = None) -> ListRegistryResponse :

        """
          1. We will store this current pagination key to be used as prev. 
          2. We will create the new request object. 
          3. We will save the old pagination keys. (Apparently dyanmo db does not have backwards pagination)
          4. We will make the pagination call to the datastore-client and retrieve the new results.
        """

        if not self.current_pagination_request:
            raise Exception("No pagination object found. Please retrieve datasets first.")

        if list_dataset_request:
            self.current_pagination_request = list_dataset_request 

        if self.current_pagination_request.pagination_key:
            self.previous_keys.append(self.current_pagination_request.pagination_key)

        pagination_response = await self._datastore_client.get_all_dataset(list_request= self.current_pagination_request)

        # Update the new pagination key
        self.current_pagination_request.pagination_key = pagination_response.pagination_key
        
        return pagination_response

    async def prev_dataset(self) -> ListRegistryResponse:

        if not self.current_pagination_request:
            raise Exception("No pagination object found. Please retrieve datasets first.")
       
        if not self.previous_keys:
            raise Exception("No previous keys found. Please retrieve datasets first. ")

        self.current_pagination_request.pagination_key = self.previous_keys.pop()
        
        pagination_response = await self._datastore_client.get_all_dataset(list_request=self.current_pagination_request)

        return pagination_response

    async def generate_dataset_presigned_url(self, dataset_presigned_request: PresignedURLRequest) -> PresignedURLResponse:
        """Generates a presigned url for an existing dataset.

        Parameters
        ----------
        dataset_presigned_request : PresignedURLRequest
            Contains the dataset id + file path + length of expiry of URL.

        Returns
        -------
        PresignedURLResponse
            A response with the presigned url.
        """

        return await self._datastore_client.generate_presigned_url(presigned_url= dataset_presigned_request)
    
    async def generate_read_access_credentials(self, credentials: CredentialsRequest) -> CredentialResponse:
        """Given an S3 location, will attempt to generate programmatic access keys for 
           the storage bucket at this particular subdirectory.

        Parameters
        ----------
        credentials : CredentialsRequest
            Contains the dataset id + console session URL required flag (boolean)

        Returns
        -------
        CredentialResponse
            The AWS credentials creating read level access into the subset of the bucket requested in the S3 location object.
        """

        return await self._datastore_client.generate_read_access_credentials(read_access_credientals= credentials)
    
    async def generate_write_access_credentials(self, credentials: CredentialsRequest) -> CredentialResponse:
        """Given an S3 location, will attempt to generate programmatic access keys for 
           the storage bucket at this particular subdirectory.

        Parameters
        ----------
        credentials : CredentialsRequest
            Contains the dataset id + console session URL required flag (boolean)

        Returns
        -------
        CredentialResponse
            The AWS credentials creating write level access into the subset of the bucket requested in the S3 location object.
        """

        return await self._datastore_client.generate_write_access_credentials(write_access_credientals= credentials)
    



    async def search_datasets(self, query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> LoadedSearchResponse:
        """

        Utilises the L2 search client to search for datasets with the specified
        query.

        Loads all datasets in the result payload from the data store and sorts
        based on auth, or other exceptions if not successful.

        Args:
            query (str): The query to make limit (int, optional): The result
            count limit. Defaults to DEFAULT_SEARCH_LIMIT.

        Returns:
            LoadedSearchResponse: The loaded items incl errors.
        """
        # search with search client
        search_results = await self._search_client.search_registry(
            query=query,
            limit=limit,
            subtype_filter=ItemSubType.DATASET
        )

        # load each result checking 401 for auth errors or misc errors recorded
        success: List[LoadedSearchItem] = []
        auth_err: List[UnauthorisedSearchItem] = []
        misc_err: List[FailedSearchItem] = []

        assert search_results.results is not None
        for item in search_results.results:
            # load item
            try:
                loaded_dataset = await self._datastore_client.fetch_dataset(
                    id=item.id
                )
                assert loaded_dataset.item
                success.append(LoadedSearchItem(
                    id=item.id,
                    item=loaded_dataset.item,
                    score=item.score
                ))
            except AuthException as e:
                auth_err.append(UnauthorisedSearchItem(
                    id=item.id,
                    score=item.score
                ))
            except Exception as e:
                misc_err.append(FailedSearchItem(
                    id=item.id,
                    score=item.score,
                    error_info=f"Failed to fetch item, error: {e}."
                ))

        return LoadedSearchResponse(
            items=success,
            auth_errors=auth_err,
            misc_errors=misc_err
        )
