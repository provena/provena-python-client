from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import DatastoreClient, SearchClient
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat, ItemSubType
from provenaclient.models import LoadedSearchResponse, LoadedSearchItem, UnauthorisedSearchItem, FailedSearchItem
from provenaclient.utils.exceptions import *
from typing import List

# L3 interface.

DEFAULT_SEARCH_LIMIT = 25


class Datastore:
    auth: AuthManager
    config: Config
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
        self.auth = auth
        self.config = config

        # Clients related to the datastore scoped as private.
        self._datastore_client = datastore_client
        self._search_client = search_client

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

        response = await self._datastore_client.fetch_dataset(id)
        return response

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

        response = await self._datastore_client.mint_dataset(dataset_mint_info)
        return response

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
                    strength=item.score
                ))
            except AuthException as e:
                auth_err.append(UnauthorisedSearchItem(
                    id=item.id,
                    strength=item.score
                ))
            except Exception as e:
                misc_err.append(FailedSearchItem(
                    id=item.id,
                    strength=item.score,
                    error_info=f"Failed to fetch item, error: {e}."
                ))

        return LoadedSearchResponse(
            items=success,
            auth_errors=auth_err,
            misc_errors=misc_err
        )