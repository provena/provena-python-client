'''
Created Date: Friday May 31st 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday May 31st 2024 9:50:26 am +1000
Modified By: Peter Baker
-----
Description: A L3 module which is setup to interact more nicely with the Username Person Link service.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Initial ideas included but is not finished/ready. Blocked by Registry API functionality.
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.modules.module_helpers import ModuleService
from provenaclient.clients import AuthClient

# L3 interface.

class Link(ModuleService):
    _auth_client: AuthClient

    def __init__(self, auth: AuthManager, config: Config, auth_client: AuthClient) -> None:
        """
        The link service L3 is a set of helper functions to interact more intuitively with the link service. 

        For example, combining looking up user link details with resolving the person. 

        Or could help to create and link person in one action.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance.
        auth_client: AuthClient 
            L2 auth client used to help with link service
        """
        # Module service
        self._auth = auth
        self._config = config

        # Clients related to the datastore scoped as private.
        self._auth_client = auth_client

    async def get_linked_person(self) -> None:
        # fetches current user link then loads person
        # TODO pseudocode below to complete once registry is implemented
        # get link
        link_result = await self._auth_client.get_link_lookup_username()

        # then load person with resulting id
        person_id = link_result.person_id
        if person_id is None:
            return None
        else:
            # TODO
            # return await self._registry_client.person.fetch(id=person_id)
            return None

    async def create_and_link_person(self) -> None:
        # TODO
        # check user is not already linked
        # check there is not already a person in registry which matches first/last name or which has matching username
        # then create person with specified details
        # then link person
        return None
