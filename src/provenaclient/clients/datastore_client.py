from provenaclient.utils.AuthManager import AuthManager
from provenaclient.utils.Config import Config
from provenaclient.utils.httpClient import HttpClient
from enum import Enum
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat
from pydantic import ValidationError
from provenaclient.utils.exceptions.AuthException import AuthException, ValidationException, ServerException
from http import HTTPStatus

class DatastoreEndpoints(Enum):
    FETCH_DATASET: str = "/registry/items/fetch-dataset"
    MINT_DATASET: str  = "/register/mint-dataset"

class DatastoreClient: 
    auth: AuthManager
    config: Config

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self.auth = auth
        self.config = config

    
    async def fetch_dataset(self, id: str) -> RegistryFetchResponse:
        
        # Prepare and setup the API request.
        get_auth = self.auth.get_async_auth # Get bearer auth
        url = self.config.datastore_api_endpoint + DatastoreEndpoints.FETCH_DATASET.value
        params = {"handle_id": id}

        try: 
            response = await HttpClient.make_get_request(url = url, params=params, auth = get_auth())

            if response.status_code != 200:

                error_message = response.json().get('detail')

                if response.status_code == 401:
                    raise AuthException(message = "Authentication failed", error_code = 401, payload = error_message)

                if response.status_code == 422:
                    # This is a specific status code of this URL.
                    raise ValidationException(message ="Validation error", error_code = 422, payload = error_message)
                
                if response.status_code >=500:
                    # Raise another exception here 
                    raise ServerException(message = "Server error occurred", error_code = response.status_code, payload = error_message )
        
        except (AuthException, ValidationException, ServerException):
            raise

        except Exception as e:
            raise ValueError(f"Failed to fetch dataset with id {id}")
        
        parsed_model = None

        try: 
            json_response = response.json()
            parsed_model = RegistryFetchResponse.parse_obj(json_response)

        except ValidationError as e:
            print("Failed to fetch this item.")

        if parsed_model is None: 
            raise ValueError(f"Parsing failed for dataset with id {id}")

        return parsed_model
    
    
    async def mint_dataset(self, dataset_info: CollectionFormat) ->  MintResponse:

        get_auth = self.auth.get_async_auth # Get bearer auth
        url = self.config.datastore_api_endpoint + DatastoreEndpoints.MINT_DATASET.value

        # Convert the payload 
        json_data = dataset_info.json()

        print(json_data, "JSONN")

        try: 
            response = await HttpClient.make_post_request(url = url, data=json_data, auth = get_auth())

            print(response, "repsonsee")

            if response.status_code != 200:

                error_message = response.json().get('detail')

                if response.status_code == 401:
                    raise AuthException(message = "Authentication failed", error_code = 401, payload = error_message)

                if response.status_code == 422:
                    # This is a specific status code of this URL.
                    raise ValidationException(message ="Validation error", error_code = 422, payload = error_message)
                
                if response.status_code >=500:
                    # Raise another exception here 
                    raise ServerException(message = "Server error occurred", error_code = response.status_code, payload = error_message )
        
        except (AuthException, ValidationException, ServerException):
            raise

        except Exception as e:
            raise ValueError(f"Failed to fetch dataset with id {id}")

        parsed_model = None

        try: 
            json_response = response.json()
            parsed_model = MintResponse.parse_obj(json_response)

        except ValidationError as e:
            print("Failed to fetch this item.")

        if parsed_model is None: 
            raise ValueError(f"Parsing failed for dataset with id {id}")

        return parsed_model



    

    #async def version_dataset(self, payload: some_obj) -> 
