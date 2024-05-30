from abc import ABC
from provenaclient.auth import AuthManager
from provenaclient.utils.config import Config


class ModuleService(ABC):
    """
    This class interface just captures that the client has an instantiated auth
    manager which allows for helper functions abstracted for L3 clients.
    """
    _auth: AuthManager
    _config: Config
