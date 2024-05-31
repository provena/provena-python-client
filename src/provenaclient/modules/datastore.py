from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import DatastoreClient, SearchClient
from ProvenaInterfaces.DataStoreAPI import *
from ProvenaInterfaces.RegistryModels import CollectionFormat, ItemSubType
from provenaclient.models import HealthCheckResponse, LoadedSearchResponse, LoadedSearchItem, UnauthorisedSearchItem, FailedSearchItem, VersionDatasetRequest, VersionDatasetResponse, RevertMetadata
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from typing import List

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
        """_summary_

        Parameters
        ----------
        reviewer_id : str
            _description_
        """
        await self._datastore_client.admin.delete_dataset_reviewer(reviewer_id=reviewer_id)

    async def add_dataset_reviewer(self, reviewer_id: str) -> None: 
        """_summary_

        Parameters
        ----------
        reviewer_id : str
            _description_

        Returns
        -------
        _type_
            _description_
        """

        await self._datastore_client.admin.add_dataset_reviewer(reviewer_id=reviewer_id)

    """
    async def list_reviewers(self) -> TODO: 
        TODO
    """

    async def dataset_approval_request(self, approval_request: ReleaseApprovalRequest) -> ReleaseApprovalRequestResponse:
        """_summary_

        Parameters
        ----------
        approval_request : ReleaseApprovalRequest
            _description_

        Returns
        -------
        ReleaseApprovalRequestResponse
            _description_
        """

        return await self._datastore_client.admin.approval_request(approval_request_payload= approval_request)
    
    async def action_approval_request(self, action_approval_request: ActionApprovalRequest)-> ActionApprovalRequestResponse:
        """_summary_

        Parameters
        ----------
        action_approval_request : ActionApprovalRequest
            _description_

        Returns
        -------
        ActionApprovalRequestResponse
            _description_
        """

        return await self._datastore_client.admin.action_approval_request(action_approval_request_payload= action_approval_request) 



class Datastore(ModuleService):
    _datastore_client: DatastoreClient
    _search_client: SearchClient

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

    async def get_health_check(self) -> HealthCheckResponse:
        """_summary_

        Returns
        -------
        HealthCheckResponse
            _description_
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
        """_summary_

        Parameters
        ----------
        metadata_payload : CollectionFormat
            _description_

        Returns
        -------
        StatusResponse
            _description_
        """

        return await self._datastore_client.validate_metadata(metadata_payload=metadata_payload)
    
    async def update_dataset_metadata(self, handle_id: str, reason: str, metadata_payload: CollectionFormat) -> UpdateMetadataResponse:
        """_summary_

        Parameters
        ----------
        handle_id : str
            _description_
        reason : str
            _description_
        metadata_payload : CollectionFormat
            _description_

        Returns
        -------
        UpdateMetadataResponse
            _description_
        """

        return await self._datastore_client.update_metadata(handle_id=handle_id, reason=reason, metadata_payload=metadata_payload)
    
    async def revert_dataset_metadata(self, metadata_payload: RevertMetadata) -> StatusResponse:
        """_summary_

        Parameters
        ----------
        metadata_payload : RevertMetadata
            _description_

        Returns
        -------
        StatusResponse
            _description_
        """

        return await self._datastore_client.revert_metadata(metadata_payload=metadata_payload)
    
    async def version_dataset(self, version_request: VersionDatasetRequest) -> VersionDatasetResponse: 
        """_summary_

        Parameters
        ----------
        version_request : VersionDatasetRequest
            _description_

        Returns
        -------
        VersionDatasetResponse
            _description_
        """

        return await self._datastore_client.version_dataset(version_dataset_payload=version_request)
    
    async def generate_dataset_presigned_url(self, dataset_presigned_request: PresignedURLRequest) -> PresignedURLResponse:
        """_summary_

        Parameters
        ----------
        dataset_presigned_request : PresignedURLRequest
            _description_

        Returns
        -------
        PresignedURLResponse
            _description_
        """

        return await self._datastore_client.generate_presigned_url(presigned_url= dataset_presigned_request)
    
    async def generate_read_access_credentials(self, credentials: CredentialsRequest) -> CredentialResponse:
        """_summary_

        Parameters
        ----------
        credentials : CredentialsRequest
            _description_

        Returns
        -------
        CredentialResponse
            _description_
        """

        return await self._datastore_client.generate_read_access_credentials(read_access_credientals= credentials)
    
    async def generate_write_access_credentials(self, credentials: CredentialsRequest) -> CredentialResponse:
        """_summary_

        Parameters
        ----------
        credentials : CredentialsRequest
            _description_

        Returns
        -------
        CredentialResponse
            _description_
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
