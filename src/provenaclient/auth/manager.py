'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: Auth Manager interface which defines key methods for authorising API requests in the provena client
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from abc import ABC, abstractmethod
from provenaclient.auth.helpers import HttpxBearerAuth
from typing import Optional, Literal
from enum import Enum
import logging


class Log(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

# Type alias so we can type the function properly using high level types
LogType = Literal[Log.DEBUG, Log.INFO, Log.WARNING, Log.ERROR]

DEFAULT_LOG_LEVEL = Log.ERROR


class AuthManager(ABC):
    # This must
    logger: logging.Logger

    def __init__(self, log_level: Optional[LogType] = None) -> None:
        # Create a logger
        self.logger = logging.getLogger('auth-logger')

        # LOGGING LEVEL
        self.logger.setLevel(
            log_level.value if log_level else DEFAULT_LOG_LEVEL.value)

        # Create a console handler and set its log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level.value if log_level else DEFAULT_LOG_LEVEL.value)

        # Create a formatter and set it for the console handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(console_handler)

    @abstractmethod
    def get_token(self) -> str:
        """Get token information and other metadata."""
        pass

    @abstractmethod
    def force_refresh(self) -> None:
        """ Force refresh the current token"""
        pass

    def get_auth(self) -> HttpxBearerAuth:
        """A helper function which produces a BearerAuth object for use
        in the httpx library. For example: 

        manager = DeviceFlow(...)
        auth = manager.get_auth 
        httpx.post(..., auth=auth)

        Returns
        -------
        BearerAuth
            The httpx auth object.

        Raises
        ------
        Exception
            Raises exception if tokens/public_key are not setup - make sure 
            that the object is instantiated properly before calling this function.
        Exception
            If the token is invalid and cannot be refreshed.
        Exception
            If the token validation still fails after re-conducting the device flow.
        """

        token = self.get_token()
        return HttpxBearerAuth(token=token)
