from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import ProvClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from typing import List

# L3 interface.

class Prov(ModuleService):
    _prov_client: ProvClient

    def __init__(self, auth: AuthManager, config: Config, prov_client: ProvClient) -> None:
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

        # Clients related to the prov-api scoped as private.
        self._prov_api_client = prov_client