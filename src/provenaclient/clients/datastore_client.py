from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
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


class DatastoreClient:

    auth: AuthManager
    config: Config

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the DatastoreClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self.auth = auth
        self.config = config

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

        # Prepare and setup the API request.
        get_auth = self.auth.get_auth  # Get bearer auth
        url = self.config.datastore_api_endpoint + DatastoreEndpoints.FETCH_DATASET
        params = {"handle_id": id}
        message = f"Failed to fetch the dataset with id {id}..."

        try:
            response = await HttpClient.make_get_request(url=url, params=params, auth=get_auth())
            data = handle_response_with_status(
                response=response,
                model=RegistryFetchResponse,
                error_message=message
            )

        except api_exceptions as e:
            raise e

        except Exception as e:
            raise Exception(
                f"{message} Exception: {e}") from e

        return data

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

        get_auth = self.auth.get_auth  # Get bearer auth
        url = self.config.datastore_api_endpoint + DatastoreEndpoints.MINT_DATASET

        # Create a payload object.
        payload_object = py_to_dict(dataset_info)
        message = f"Failed to mint the desired dataset..."

        try:
            response = await HttpClient.make_post_request(url=url, data=payload_object, auth=get_auth())
            data = handle_response_with_status(
                response=response,
                model=MintResponse,
                error_message=message
            )
        except api_exceptions as e:
            raise e
        except Exception as e:
            raise Exception(
                f"{message} Exception: {e}") from e

        return data
