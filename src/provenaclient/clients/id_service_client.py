'''
Created Date: Friday May 31st 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday May 31st 2024 9:50:26 am +1000
Modified By: Peter Baker
-----
Description: ID/Handle service L2 Client
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Noting that the models published for the endpoints are not being detected in Swagger docs due to a type Alias being used
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from ProvenaInterfaces.HandleAPI import *


class IdServiceEndpoints(str, Enum):
    """An ENUM containing the handle api endpoints."""
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    POST_HANDLE_MINT = "/handle/mint"
    POST_HANDLE_ADD_VALUE = "/handle/add_value"
    POST_HANDLE_ADD_VALUE_BY_INDEX = "/handle/add_value_by_index"
    GET_HANDLE_GET = "/handle/get"
    GET_HANDLE_LIST = "/handle/list"
    PUT_HANDLE_MODIFY_BY_INDEX = "/handle/modify_by_index"
    POST_HANDLE_REMOVE_BY_INDEX = "/handle/remove_by_index"
    GET_HEALTH_CHECK = "/"

# L2 interface.


class IdServiceClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the IdServiceClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: IdServiceEndpoints) -> str:
        return self._config.handle_service_api_endpoint + endpoint.value

    async def mint(self, body: MintRequest) -> Handle:
        """
        
        Mints a new handle with given properties.

        Args:
            body (MintRequest): The payload

        Returns:
            Handle: The resulting handle object
        """
        return await parsed_post_request(
            client=self,
            params={},
            json_body=py_to_dict(body),
            url=self._build_endpoint(IdServiceEndpoints.POST_HANDLE_MINT),
            model=Handle,
            error_message=f"Failed to mint new handle."
        )
        
    async def add_value(self, body: AddValueRequest) -> Handle:
        """
        Adds value to a handle.

        Args:
            body (AddValueRequest): The value to add

        Returns:
            Handle: The handle object
        """
        return await parsed_post_request(
            client=self,
            params={},
            json_body=py_to_dict(body),
            url=self._build_endpoint(IdServiceEndpoints.POST_HANDLE_ADD_VALUE),
            model=Handle,
            error_message=f"Failed to add value to handle."
        )
        
    async def add_value_by_index(self, body: AddValueIndexRequest) -> Handle:
        """
        Adds a value at specified index

        Args:
            body (AddValueIndexRequest): The value to add

        Returns:
            Handle: The handle object
        """
        return await parsed_post_request(
            client=self,
            params={},
            json_body=py_to_dict(body),
            url=self._build_endpoint(IdServiceEndpoints.POST_HANDLE_ADD_VALUE_BY_INDEX),
            model=Handle,
            error_message=f"Failed to add value by index to handle."
        )

    async def list(self) -> ListResponse:
        """
        Lists all handles under domain.

        Returns:
            ListResponse: The response list
        """
        return await parsed_get_request(
            client=self,
            params={},
            url=self._build_endpoint(IdServiceEndpoints.GET_HANDLE_LIST),
            model=ListResponse,
            error_message=f"Failed to list handles."
        )
        
    async def modify_by_index(self, body: ModifyRequest) -> Handle:
        """
        Modifies existing handle value at specified index

        Args:
            body (ModifyRequest): The request to modify

        Returns:
            Handle: The handle object
        """ 
        return await parsed_post_request(
            client=self,
            params={},
            json_body=py_to_dict(body),
            url=self._build_endpoint(IdServiceEndpoints.PUT_HANDLE_MODIFY_BY_INDEX),
            model=Handle,
            error_message=f"Failed to modify property by index."
        )
        
    async def remove_by_index(self, body: RemoveRequest) -> Handle:
        """
        
        Removes value at specified index

        Args:
            body (RemoveRequest): The removal request

        Returns:
            Handle: The handle object
        """
        return await parsed_post_request(
            client=self,
            params={},
            json_body=py_to_dict(body),
            url=self._build_endpoint(IdServiceEndpoints.POST_HANDLE_REMOVE_BY_INDEX),
            model=Handle,
            error_message=f"Failed to remove property by index."
        )