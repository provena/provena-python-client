'''
Created Date: Thursday May 30th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday May 30th 2024 10:17:36 am +1000
Modified By: Peter Baker
-----
Description: A template file for creating an L3 module.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

# from provenaclient.auth.manager import AuthManager
# from provenaclient.utils.config import Config
# from pydantic import BaseModel
#
# L3 interface.
#
# class REPLACE(ModuleService):
#    _replace_client: REPLACEClient
#
#    def __init__(self, auth: AuthManager, config: Config, replace_client: REPLACEClient) -> None:
#        """
#
#        TODO
#
#        Parameters
#        ----------
#        auth : AuthManager
#            An abstract interface containing the user's requested auth flow
#            method.
#        config : Config
#            A config object which contains information related to the Provena
#            instance.
#        """
#        # Module service
#        self._auth = auth
#        self._config = config
#
#        # Clients related to the datastore scoped as private.
#        self._replace_client = replace_client
#
#    async def example_method(self) -> BaseModel:
#        return await self._replace_client.example()
#
