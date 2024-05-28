from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients.datastore_client import DatastoreClient
from provenaclient.modules.datastore import Datastore

#L3 interface.

class ProvenaClient():
    auth: AuthManager 
    config: Config

    # private clients L2
    _datastore_client: DatastoreClient

    # Modules
    datastore: Datastore

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self.auth = auth
        self.config = config

        self._datastore_client = DatastoreClient(auth, config)

        self.datastore = Datastore(auth=auth, config=config, datastore_client=self._datastore_client)