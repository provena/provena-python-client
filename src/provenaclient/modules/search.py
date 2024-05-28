from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import SearchClient
from ProvenaInterfaces.RegistryModels import ItemSubType
from ProvenaInterfaces.SearchAPI import QueryResults
from typing import Optional

# L3 interface.

DEFAULT_SEARCH_LIMIT = 25


class Search:
    auth: AuthManager
    config: Config
    _search_client: SearchClient

    def __init__(self, auth: AuthManager, config: Config, search_client: SearchClient) -> None:
        """

        Initialises a new search object, which sits between the user and the
        search api operations.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance. 
        search_client : SearchClient
            This client interacts with the Search Client's API's.
        """
        self.auth = auth
        self.config = config

        # Clients related to the datastore scoped as private.
        self._search_client = search_client

    async def search_registry(self, query: str, limit: Optional[int], subtype_filter: Optional[ItemSubType]) -> QueryResults:
        """

        Searches the registry for given query, limit and subtype.

        Args:
            query (str): The query to make
            limit (Optional[int]): The query limit
            subtype_filter (Optional[ItemSubType]): The subtype to filter by if any

        Returns:
            QueryResults: Results - ids and scores
        """
        return await self._search_client.search_registry(
            limit=limit, query=query, subtype_filter=subtype_filter
        )
