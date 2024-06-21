'''
Created Date: Friday May 31st 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday May 31st 2024 9:50:26 am +1000
Modified By: Peter Baker
-----
Description: The main Provena L3 client class which collects sub L2 clients and L3 clients.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Cleaned up and added missing modules.
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import *
from provenaclient.modules import *
from provenaclient.modules.module_helpers import *

# L3 interface.


class ProvenaClient(ModuleService):
    # L2 + L3 combinations

    # Data store
    _datastore_client: DatastoreClient
    datastore: Datastore
    
    # Search 
    _search_client: SearchClient
    search: Search
    
    # Auth 
    _auth_client: AuthClient
    auth_api: Auth
    
    # Registry 
    _registry_client: RegistryClient
    registry: Registry
    
    # Prov 
    _prov_client: ProvClient
    prov_api: Prov
    
    # Jobs 
    _job_client: JobAPIClient
    job_api: JobService
    
    # ID service 
    _id_client: IdServiceClient
    id_api: IDService

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """
        
        Build an instance of the Provena Client.

        Args:
            auth (AuthManager): The Auth implementation to use. See auth.implementations
            config (Config): The provena config which indicates deployment and other settings
        """
        # Module service
        self._auth = auth
        self._config = config

        # (L2 clients)
        self._datastore_client = DatastoreClient(auth, config)
        self._search_client = SearchClient(auth, config)
        self._auth_client = AuthClient(auth, config)
        self._registry_client = RegistryClient(auth, config)
        self._prov_client = ProvClient(auth, config)
        self._job_client = JobAPIClient(auth,config)
        self._id_client = IdServiceClient(auth,config)

        self.datastore = Datastore(
            auth=auth,
            config=config,
            datastore_client=self._datastore_client,
            search_client=self._search_client
        )

        self.search = Search(
            auth=auth,
            config=config,
            search_client=self._search_client
        )

        self.auth_api = Auth(
            auth=auth,
            config=config,
            auth_client=self._auth_client
        )

        self.registry = Registry(
            auth=auth, 
            config=config,
            registry_client=self._registry_client
        )

        self.prov_api = Prov(
            auth=auth, 
            config=config, 
            prov_client=self._prov_client
        )
        
        self.job_api = JobService(
            auth=auth, 
            config=config, 
            job_api_client=self._job_client
        )
        
        self.id_api = IDService(
            auth=auth, 
            config=config, 
            id_service_client=self._id_client
        )