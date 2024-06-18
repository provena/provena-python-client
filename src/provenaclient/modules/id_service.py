'''
Created Date: Friday May 31st 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday May 31st 2024 9:50:26 am +1000
Modified By: Peter Baker
-----
Description: The ID Service L3 module.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import IdServiceClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from ProvenaInterfaces.HandleAPI import *

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

    async def mint(self, body: MintRequest) -> Handle:
        """

        Mints a new handle with given properties.

        Args:
            body (MintRequest): The payload

        Returns:
            Handle: The resulting handle object
        """
        return await self._id_service_client.mint(body=body)

    async def add_value(self, body: AddValueRequest) -> Handle:
        """
        Adds value to a handle.

        Args:
            body (AddValueRequest): The value to add

        Returns:
            Handle: The handle object
        """
        return await self._id_service_client.add_value(body=body)

    async def add_value_by_index(self, body: AddValueIndexRequest) -> Handle:
        """
        Adds a value at specified index

        Args:
            body (AddValueIndexRequest): The value to add

        Returns:
            Handle: The handle object
        """
        return await self._id_service_client.add_value_by_index(body=body)

    async def list(self) -> ListResponse:
        """
        Lists all handles under domain.

        Returns:
            ListResponse: The response list
        """
        return await self._id_service_client.list()

    async def modify_by_index(self, body: ModifyRequest) -> Handle:
        """
        Modifies existing handle value at specified index

        Args:
            body (ModifyRequest): The request to modify

        Returns:
            Handle: The handle object
        """
        return await self._id_service_client.modify_by_index(body=body)

    async def remove_by_index(self, body: RemoveRequest) -> Handle:
        """

        Removes value at specified index

        Args:
            body (RemoveRequest): The removal request

        Returns:
            Handle: The handle object
        """
        return await self._id_service_client.remove_by_index(body=body)
