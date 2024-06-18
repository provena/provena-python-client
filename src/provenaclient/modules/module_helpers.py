'''
Created Date: Thursday May 30th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday May 30th 2024 10:17:36 am +1000
Modified By: Peter Baker
-----
Description: Defines L3 module level helpers, notably a common interface for the ModuleService.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Noting this might not be a great place to host this interface.
'''

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
