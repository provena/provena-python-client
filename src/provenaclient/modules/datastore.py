from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients.datastore_client import DatastoreClient
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat, CollectionFormatApprovals, CollectionFormatDatasetInfo, CollectionFormatAssociations

# L3 interface.


class Datastore:
    auth: AuthManager
    config: Config
    _datastore_client: DatastoreClient

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient) -> None:
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
