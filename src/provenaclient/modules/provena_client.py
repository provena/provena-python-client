from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import *
from provenaclient.modules import *

# L3 interface.


class ProvenaClient():
    auth: AuthManager
    config: Config

    # private clients L2
    _datastore_client: DatastoreClient
    _search_client: SearchClient

    # Modules
    datastore: Datastore
    search: Search

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self.auth = auth
        self.config = config

        self._datastore_client = DatastoreClient(auth, config)
        self._search_client = SearchClient(auth, config)

        self.datastore = Datastore(
            auth=auth,
            config=config,
            datastore_client=self._datastore_client,
            search_client=self._search_client
        )
