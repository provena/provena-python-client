from ..utils.AuthManager  import AuthManager
from ..utils.Config import Config
from ..clients.DatastoreClient import DatastoreClient
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse


class Datastore: 
    auth: AuthManager
    config: Config

    datastore_client: DatastoreClient

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient) -> None:
        self.auth = auth
        self.config = config
        # Clients related to the datastore scoped as private.
        self._datastore_client = datastore_client  
    
    async def fetch_item(self, id:str) -> RegistryFetchResponse:

        try: 
            response = await self._datastore_client.fetch_dataset(id)
        
        except Exception as e:
            raise Exception(f"Failed due too.. {e}")
        
        return response

