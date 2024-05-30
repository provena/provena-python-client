from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import *
from provenaclient.modules import *
from provenaclient.modules.module_helpers import *

# L3 interface.


class ProvenaClient(ModuleService):
    # private clients L2
    _datastore_client: DatastoreClient
    _search_client: SearchClient
    _auth_client: AuthClient

    # Modules
    datastore: Datastore
    search: Search
    auth_api: Auth
    link: Link

    def __init__(self, auth: AuthManager, config: Config) -> None:
        # Module service
        self._auth = auth
        self._config = config

        # (L2 clients)
        self._datastore_client = DatastoreClient(auth, config)
        self._search_client = SearchClient(auth, config)
        self._auth_client = AuthClient(auth, config)

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
        
        self.link = Link(
            auth=auth,
            config=config,
            auth_client=self._auth_client
        )
