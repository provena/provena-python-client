from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import HandleServiceClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from typing import List

# L3 interface.

class HandleService(ModuleService):
    _handle_service_client: HandleServiceClient

    def __init__(self, auth: AuthManager, config: Config, handle_service_client: HandleServiceClient) -> None:
        """Initialises a new datastore object, which sits between the user and the datastore api operations.

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
        self.handle_service_client = handle_service_client