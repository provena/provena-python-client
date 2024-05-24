from provenaclient.auth.auth_manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
from enum import Enum
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat
from provenaclient.utils.exceptions import ValidationException, BadRequestException, CustomTimeoutException
from provenaclient.utils.helpers import py_to_dict, api_exceptions, handle_model_parsing, handle_response, ValidationError, parse_response_to_json
from httpx import TimeoutException

class DatastoreEndpoints(str,Enum):
    """An ENUM containing the datastore-api
    endpoints.
    """
    FETCH_DATASET: str = "/registry/items/fetch-dataset"
    MINT_DATASET: str  = "/register/mint-dataset"

#L2 interface.

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
        get_auth = self.auth.get_auth # Get bearer auth
        url = self.config.datastore_api_endpoint + DatastoreEndpoints.FETCH_DATASET
        params = {"handle_id": id}

        try: 
            response = await HttpClient.make_get_request(url = url, params=params, auth = get_auth())
            response_parsed, parsed_status = parse_response_to_json(response = response)

            if response.status_code != 200:
                error_message = parsed_status.status.details
                handle_response(response=response, error_message=error_message)
        
        except api_exceptions as e:
            raise e

        except TimeoutException:
            raise CustomTimeoutException("Your request has timed out.", url = url)

        except Exception as e:
            raise Exception(f"Failed to fetch dataset with id {id}. Exception: {e}") from e  # Signifies that this exception is being raised from a parent.
        
        try:
            parsed_model = handle_model_parsing(response=response_parsed, model= RegistryFetchResponse) 

        except ValidationError as e:
            raise Exception(f"Failed to parse the fetched dataset with id {id}. Exception: {e} ") from e

        return parsed_model
    
    async def mint_dataset(self, dataset_info: CollectionFormat) ->  MintResponse:
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

        get_auth = self.auth.get_auth # Get bearer auth
        url = self.config.datastore_api_endpoint + DatastoreEndpoints.MINT_DATASET

        # Create a payload object.
        payload_object = py_to_dict(dataset_info)

        try: 
            response = await HttpClient.make_post_request(url = url, data=payload_object, auth = get_auth())
            response_parsed, parsed_status = parse_response_to_json(response = response)

            if response.status_code != 200:
                
                error_message = parsed_status.status.details
                handle_response(response=response, error_message=error_message)
            
            if response.status_code == 200 and parsed_status.status.success == False:

                error_message = parsed_status.status.details
                raise BadRequestException(message="Bad Request", error_code= 400, payload= error_message)

        except api_exceptions as e:
            raise e

        except TimeoutException:
            raise CustomTimeoutException(message = "Your request has timed out.", url = url)

        except Exception as e:
            raise Exception(f"Failed to create dataset. Exception {e}") from e

        try:
            parsed_model = handle_model_parsing(response=response_parsed, model= MintResponse)

        except ValidationError as e:
            raise ValidationException(f"Failed to parse the created dataset. Exception: {e} ") from e

        return parsed_model