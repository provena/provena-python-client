from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
from enum import Enum
from ProvenaInterfaces.RegistryModels import ItemSubType
from ProvenaInterfaces.SearchAPI import QueryResults
from provenaclient.utils.helpers import *


class SearchEndpoints(str, Enum):
    """An ENUM containing the datastore-api
    endpoints.
    """
    SEARCH_REGISTRY: str = "/search/entity-registry"

# L2 interface.


class SearchClient:

    auth: AuthManager
    config: Config

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the SearchClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self.auth = auth
        self.config = config

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
        # Prepare and setup the API request.
        get_auth = self.auth.get_auth  # Get bearer auth
        url = self.config.search_api_endpoint + SearchEndpoints.SEARCH_REGISTRY
        params = build_params_exclude_none(
            {"query": query, "record_limit": limit, "subtype_filter": subtype_filter.value if subtype_filter else None})
        message = f"Search with query '{query}' failed!..."

        try:
            response = await HttpClient.make_get_request(url=url, params=params, auth=get_auth())
            data = handle_response_with_status(
                response=response,
                model=QueryResults,
                error_message=message
            )

        except api_exceptions as e:
            raise e

        except Exception as e:
            raise Exception(
                f"{message} Exception: {e}") from e
            
        return data