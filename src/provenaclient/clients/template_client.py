# from provenaclient.auth.manager import AuthManager
# from provenaclient.utils.config import Config
# from provenaclient.utils.http_client import HttpClient
# from enum import Enum
# from provenaclient.utils.helpers import *
# from provenaclient.clients.client_helpers import *
#
#
# class REPLACEEndpoints(str, Enum):
#    """An ENUM containing the REPLACE endpoints.
#    """
#    REPLACE_ENDPOINT: str = "TODO"
#
# L2 interface.
#
#
# class REPLACEClient(ClientService):
#    def __init__(self, auth: AuthManager, config: Config) -> None:
#        """Initialises the REPLACEClient with authentication and configuration.
#
#        Parameters
#        ----------
#        auth : AuthManager
#            An abstract interface containing the user's requested auth flow method.
#        config : Config
#            A config object which contains information related to the Provena instance.
#        """
#        self._auth = auth
#        self._config = config

#    def _build_endpoint(self, endpoint: REPLACEEndpoints) -> str:
#        return self._config.replace_api_endpoint + endpoint.value
#
#    async def example_method(self) -> BaseModel:
#        return await parsed_get_request(
#            client=self,
#            url=self._build_endpoint(REPLACEEndpoints.TODO),
#            error_message="TODO",
#            params={},
#            model=BaseModel
#        )
