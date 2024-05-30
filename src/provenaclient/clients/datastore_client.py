from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients.client_helpers import *
from enum import Enum
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat
from provenaclient.utils.helpers import *


class DatastoreEndpoints(str, Enum):
    """An ENUM containing the datastore-api
    endpoints.
    """
    FETCH_DATASET: str = "/registry/items/fetch-dataset"
    MINT_DATASET: str = "/register/mint-dataset"

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
                DatastoreEndpoints.FETCH_DATASET),
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
            url=self._build_endpoint(DatastoreEndpoints.MINT_DATASET),
            error_message="Failed to mint the desired dataset...",
            params={},
            json_body=py_to_dict(dataset_info),
            model=MintResponse
        )
