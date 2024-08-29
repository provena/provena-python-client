'''
Created Date: Thursday June 6th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday June 6th 2024 1:39:55 pm +1000
Modified By: Peter Baker
-----
Description: Datastore L3 module. Includes the Data store review sub module.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

29-08-2024 | Parth Kulkarni | Added Downloading Specific file/directory functionality to interactive class.
22-08-2024 | Parth Kulkarni | Completed Interactive Dataset class + Doc Strings. 
15-08-2024 | Parth Kulkarni | Added a prototype/draft of the Interactive Dataset Class. 

'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import DatastoreClient, SearchClient
from ProvenaInterfaces.DataStoreAPI import *
from ProvenaInterfaces.RegistryModels import CollectionFormat, ItemSubType
from provenaclient.models import HealthCheckResponse, LoadedSearchResponse, LoadedSearchItem, UnauthorisedSearchItem, FailedSearchItem, RevertMetadata
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from ProvenaInterfaces.RegistryAPI import NoFilterSubtypeListRequest, VersionRequest, VersionResponse, SortOptions, DatasetListResponse
from provenaclient.modules.submodules import IOSubModule

from typing import AsyncGenerator, List

# L3 interface.

DEFAULT_SEARCH_LIMIT = 25
DATASTORE_DEFAULT_SEARCH_LIMIT = 20


class ReviewSubModule(ModuleService):
    _datastore_client: DatastoreClient

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient) -> None:
        """
        System reviewer sub module of the Datastore API functionality

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
        await self._datastore_client.review.delete_dataset_reviewer(reviewer_id=reviewer_id)

    async def add_dataset_reviewer(self, reviewer_id: str) -> None:
        """Add a reviewer.

        Parameters
        ----------
        reviewer_id : str
            Id of a reviewer.

        """

        await self._datastore_client.review.add_dataset_reviewer(reviewer_id=reviewer_id)

    """
    async def list_reviewers(self) -> TODO: 
        TODO

    Leaving this for now,as the pydantic response model of this endpoint will be duly updated.
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

        return await self._datastore_client.review.approval_request(approval_request_payload=approval_request)

    async def action_approval_request(self, action_approval_request: ActionApprovalRequest) -> ActionApprovalRequestResponse:
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

        return await self._datastore_client.review.action_approval_request(action_approval_request_payload=action_approval_request)


class InteractiveDataset(ModuleService):

    dataset_id: str
    auth: AuthManager
    datastore_client: DatastoreClient
    io: IOSubModule

    def __init__(self, dataset_id: str, auth: AuthManager, datastore_client: DatastoreClient, io: IOSubModule) -> None:
        """Initialise an interactive dataset session. 

        Parameters
        ----------
        dataset_id : str
            The unique identifier of the dataset to interact with.
        datastore_client : DatastoreClient
            The client responsible for interacting with the datastore API.
        io : IOSubModule
            The input/output submodule for handling dataset IO operations.
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        """

        self.dataset_id = dataset_id
        self._auth = auth
        self._datastore_client = datastore_client
        self.io = io

    async def fetch_dataset(self) -> RegistryFetchResponse :
        """Fetches current dataset from the datastore.

        Returns
        -------
        RegistryFetchResponse
            A interactive python datatype of type RegistryFetchResponse
            containing the dataset details.

        """

        return await self._datastore_client.fetch_dataset(id=self.dataset_id)
    
    async def download_all_files(self, destination_directory: str) -> None: 
        """
        Downloads all files to the destination path for your current dataset.

        - Fetches info
        - Fetches creds
        - Uses s3 cloud path lib to download all files to specified location

        Parameters:
        ---------
        destination_directory (str): 
            The destination path to save files to - use a directory
        """

        return await self.io.download_all_files(destination_directory=destination_directory, dataset_id=self.dataset_id)
    
    async def upload_all_files(self, source_directory: str) -> None: 
        """
        Uploads all files in the source path to the current dataset's storage location.

        - Fetches info
        - Fetches creds
        - Uses s3 cloud path lib to upload all files to specified location

        Parameters
        ----------
        source_directory (str): 
            The source path to upload files from - use a directory
        """

        return await self.io.upload_all_files(source_directory=source_directory, dataset_id=self.dataset_id)
    
    async def version(self, reason: str) -> VersionResponse:
        """Versioning operation which creates a new version from the current dataset.

        Parameters
        ----------
        reason : str
            The reason for versioning this dataset.
        Returns
        -------
        VersionResponse
            Response of the versioning of the dataset, containing new version ID and 
            job session ID.
        """

        version_request: VersionRequest = VersionRequest(
            id = self.dataset_id, 
            reason = reason
        )

        return await self._datastore_client.version_dataset(version_dataset_payload=version_request)
    
    async def revert_dataset_metadata(self, history_id: int, reason: str) -> StatusResponse:
        """Reverts the metadata for the current dataset to a previous identified historical version.

        Parameters
        ----------
        history_id : int
            The identifier of the historical version to revert to.
        reason : str
            The reason for reverting the dataset's metadata.

        Returns
        -------
        StatusResponse
            Response indicating whether your dataset metadata revert request was successful.
        """

        revert_request: RevertMetadata = RevertMetadata(
            id=self.dataset_id, 
            history_id=history_id,
            reason=reason
        )

        return await self._datastore_client.revert_metadata(metadata_payload=revert_request)
    
    async def generate_read_access_credentials(self, console_session_required: bool) -> CredentialResponse:
        """Given an S3 location, will attempt to generate programmatic access keys for 
           the storage bucket at this particular subdirectory.

        Parameters
        ----------
        console_session_required : bool
            Specifies whether a console session URL is required.
            
        Returns
        -------
        CredentialResponse
            The AWS credentials creating read level access into the subset of the bucket requested in the S3 location object.
        """

        credentials_request = CredentialsRequest(
            dataset_id=self.dataset_id, 
            console_session_required=console_session_required
        )

        return await self._datastore_client.generate_read_access_credentials(read_access_credentials=credentials_request)

    async def generate_write_access_credentials(self, console_session_required: bool) -> CredentialResponse:
        """Given an S3 location, will attempt to generate programmatic access keys for 
           the storage bucket at this particular subdirectory.

        Parameters
        ----------
        console_session_required : bool
            Specifies whether a console session URL is required.

        Returns
        -------
        CredentialResponse
            The AWS credentials creating write level access into the subset of the bucket requested in the S3 location object.
        """

        credentials_request = CredentialsRequest(
            dataset_id=self.dataset_id, 
            console_session_required=console_session_required
        )

        return await self._datastore_client.generate_write_access_credentials(write_access_credentials=credentials_request)
    
    async def download_specific_file(self, s3_path: str, destination_directory: str) -> None: 
        """
        Downloads a specific file or folder for the current dataset 
        from an S3 bucket to a provided destination path.

        This method handles various cases:
        - If `s3_path` is a specific file, it downloads that file directly to `destination_directory`.
        - If `s3_path` is a folder (without a trailing slash), it downloads the entire folder and its contents,
        preserving the folder structure in `destination_directory`.
        - If `s3_path` is a folder (with a trailing slash), it downloads all contents (including subfolders) within that folder but not the
        folder itself to `destination_directory`.

        Parameters
        ----------
        s3_path : str
            The S3 path of the file or folder to download. 
            - If this is a specific file, it will download just that file.
            - If this is a folder without a trailing slash (e.g., 'nested'), it will download the entire folder 
            and all its contents, preserving the structure.
            - If this is a folder with a trailing slash (e.g., 'nested/'), it will download all contents within 
            that folder but not the folder itself unless subfolders are present.
        destination_directory : str
            The destination path to save files to - use a directory.

        """

        # Calls the function in IO sub module.
        await self.io.download_specific_file(dataset_id=self.dataset_id, 
                                              s3_path=s3_path, 
                                              destination_directory=destination_directory)

class Datastore(ModuleService):
    _datastore_client: DatastoreClient
    _search_client: SearchClient

    # sub modules
    review: ReviewSubModule
    io: IOSubModule

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient, search_client: SearchClient) -> None:
        """Initialise a new datastore object, which sits between the user and the datastore api operations.

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
        self.review = ReviewSubModule(
            auth=auth,
            config=config,
            datastore_client=self._datastore_client
        )

        self.io = IOSubModule(
            auth=auth,
            config=config,
            datastore_client=self._datastore_client
        )

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

    async def version_dataset(self, version_request: VersionRequest) -> VersionResponse:
        """Versioning operation which creates a new version from the specified ID.

        Parameters
        ----------
        version_request : VersionRequest
            The request which includes the item ID and reason for versioning.

        Returns
        -------
        VersionResponse
            Response of the versioning of the dataset, containing new version ID and 
            job session ID.
        """

        return await self._datastore_client.version_dataset(version_dataset_payload=version_request)

    async def for_all_datasets(self, list_dataset_request: NoFilterSubtypeListRequest, total_limit: Optional[int] = None) -> AsyncGenerator[ItemDataset, None]:
        """Fetches all datasets based on the provided datasets in datastore based on 
            the provided sorting criteria, pagination key and page size. 

        Parameters
        ----------
        list_dataset_request : NoFilterSubtypeListRequest
            A request object configured with sorting options, pagination keys, 
            and page size that defines how datasets are queried from the datastore. 
        total_limit : Optional[int], optional
            A maximum number of datasets to fetch. If specified, the generator will 
            stop yielding datasets once this limit is reached. 
            If None, it will fetch datasets until there are no more to fetch.

        Returns
        -------
        AsyncGenerator[ItemDataset, None]
            An asynchronous generator yielding "ItemDataset"
            object which is an individual dataset from the datastore.

        Yields
        ------
        Iterator[AsyncGenerator[ItemDataset, None]]
            Each yield provides a "ItemDataset" containing an individual dataset.

        """

        total_fetched = 0

        while True:
            response = await self._datastore_client.list_datasets(list_request=list_dataset_request)

            # We will keep track of the total numbers of items fetched in the request from the API itself.
            if response.items:
                for dataset in response.items:
                    if total_limit is not None and total_fetched >= total_limit:
                        return
                    yield dataset
                    total_fetched = total_fetched + 1
            else:
                # If there are issues with gathering responses, we will increment based on the page size.
                total_fetched = total_fetched + list_dataset_request.page_size

            if response.pagination_key is None:
                break

            # Update the pagination key for the next set of requests.
            list_dataset_request.pagination_key = response.pagination_key

    async def list_datasets(self, list_dataset_request: NoFilterSubtypeListRequest) -> DatasetListResponse:
        """Takes a specific dataset list request and returns the response.

        Parameters
        ----------
        list_dataset_request : NoFilterSubtypeListRequest
            A request object configured with sorting options, pagination keys, 
            and page size that defines how datasets are queried from the datastore. 

        Returns
        -------
        DatasetListResponse
            Response containing the requested datasets in the datastore 
            based on sort criteria and page size, and contains other attributes
            such as total_item_counts and optional pagination key.
        """

        datasets = await self._datastore_client.list_datasets(list_request=list_dataset_request)
        return datasets

    async def list_all_datasets(self, sort_criteria: Optional[SortOptions] = None) -> List[ItemDataset]:
        """Fetches all datasets from the datastore and you may provide your own sort criteria.
        By default uses display name sort criteria. 

        Parameters
        ----------
        sort_criteria : Optional[SortOptions]
            An object configured with sorting options that you want 
            when displaying all datasets within the datastore.

        Returns
        -------
        List[ItemDataset]
            A list of all datasets in the datastore, sorted as requested.
        """

        list_dataset_request: NoFilterSubtypeListRequest = NoFilterSubtypeListRequest(
            sort_by=sort_criteria,
            pagination_key=None,
            page_size=DATASTORE_DEFAULT_SEARCH_LIMIT
        )

        combined_dataset_list: List[ItemDataset] = []

        while True:
            response = await self._datastore_client.list_datasets(list_request=list_dataset_request)

            if response.items:
                combined_dataset_list.extend(response.items)

            if response.pagination_key is None:
                break

            # Update the pagination key for the next request
            list_dataset_request.pagination_key = response.pagination_key

        return combined_dataset_list

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

        return await self._datastore_client.generate_presigned_url(presigned_url=dataset_presigned_request)

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

        return await self._datastore_client.generate_read_access_credentials(read_access_credentials=credentials)

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

        return await self._datastore_client.generate_write_access_credentials(write_access_credentials=credentials)

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
    
    async def interactive_dataset(self, dataset_id: str) -> InteractiveDataset:
        """Creates an interactive "session" with a dataset that allows you 
        to perform further operations without re-supplying dataset id and 
        creating objects required for other methods.

        Parameters
        ----------
        dataset_id : str
            The unique identifier of the dataset to be retrieved.
            For example: "10378.1/1451860"

        Returns
        -------
        InteractiveDataset
            An instance that allows you to perform various operations on the provided dataset. 
        """

        return InteractiveDataset(
            dataset_id=dataset_id, 
            datastore_client=self._datastore_client, 
            io = self.io,
            auth = self._auth
        )