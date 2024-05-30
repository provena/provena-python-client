from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import IdServiceClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from typing import List

# L3 interface.

class IDService(ModuleService):
    _id_service_client: IdServiceClient

    def __init__(self, auth: AuthManager, config: Config, id_service_client: IdServiceClient) -> None:
        """Initialises a new id-service object, which sits between the user and the id-service api operations.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance. 
        datastore_client : DatastoreClient
            This client interacts with the Datastore API's.
        """
        self._auth = auth
        self._config = config

        # Clients related to the handle-api scoped as private.
        self.id_service_client = id_service_client