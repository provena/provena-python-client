from ..utils.AuthManager import AuthManager
from ..utils.Config import Config
from ..utils.httpClient import HttpClient
from enum import Enum
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse
from pydantic import ValidationError

class DatastoreEndpoints(Enum):
    FETCH_DATASET: str = "/registry/items/fetch-dataset"

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

            print(response.json(), "response")

            if response.status_code != 200:
                if response.status_code == 401:
                    # Here have to define exceptions for common scenarios. 
                    pass
                
                if response.status_code >=500:
                    # Raise another exception here 
                    pass
        
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
