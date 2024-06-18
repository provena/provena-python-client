'''
Created Date: Thursday May 30th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday May 30th 2024 10:17:36 am +1000
Modified By: Peter Baker
-----
Description: Search API L2 Client.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from enum import Enum
from ProvenaInterfaces.RegistryModels import ItemSubType
from ProvenaInterfaces.SearchAPI import QueryResults
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *


class SearchEndpoints(str, Enum):
    """An ENUM containing the datastore-api
    endpoints.
    """
    SEARCH_REGISTRY: str = "/search/entity-registry"

# L2 interface.
class SearchClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the SearchClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: SearchEndpoints) -> str:
        return self._config.search_api_endpoint + endpoint.value

    async def search_registry(self, query: str, limit: Optional[int], subtype_filter: Optional[ItemSubType]) -> QueryResults:
        """

        Searches registry using search API for given query, limit and subtype.

        Args:
            query (str): The query
            limit (Optional[int]): The record result limit
            subtype_filter (Optional[ItemSubType]): The subtype to filter if desired

        Raises:
            e: Generic exceptions as usual

        Returns:
            QueryResults: The results, not loaded.
        """
        return await parsed_get_request_with_status(
            client=self,
            url=self._build_endpoint(
                SearchEndpoints.SEARCH_REGISTRY),
            error_message=f"Search with query '{query}' failed!...",
            params={"query": query, "record_limit": limit, "subtype_filter": subtype_filter.value if subtype_filter else None},
            model=QueryResults
        )