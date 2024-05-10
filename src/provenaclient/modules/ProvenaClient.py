#TODO

from ..utils.AuthManager import AuthManager
from ..utils.Config import Config
from ..clients.DatastoreClient import DatastoreClient
from ..modules.Datastore import Datastore

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