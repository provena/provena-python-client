from ..utils.AuthManager  import AuthManager
from ..utils.Config import Config
from ..clients.datastore_client import DatastoreClient
from ProvenaInterfaces.DataStoreAPI import RegistryFetchResponse, MintResponse
from ProvenaInterfaces.RegistryModels import CollectionFormat, CollectionFormatApprovals, CollectionFormatDatasetInfo,CollectionFormatAssociations


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
    
    async def mint_dataset(self, associations: CollectionFormatAssociations , approvals: CollectionFormatApprovals, dataset_info: CollectionFormatDatasetInfo) -> MintResponse: 

        if associations is None or approvals is None or dataset_info is None: 
            print("Cannot procced further, please provide the correct parameters.")
            return

        # Payload object.
        collection_format = CollectionFormat(
            associations=associations, 
            approvals=approvals,
            dataset_info=dataset_info
        )

        try:
            response = await self._datastore_client.mint_dataset(collection_format)

        except Exception as e:
            raise Exception(f"Failed due too.. {e}")
        
        return response
    








        




