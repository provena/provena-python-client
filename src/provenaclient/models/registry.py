from enum import Enum
from typing import List

class RouteActions(str, Enum):
    FETCH = "FETCH"
    LIST = "LIST"
    SEED = "SEED"
    UPDATE = "UPDATE"
    CREATE = "CREATE"
    REVERT = "REVERT"
    SCHEMA = "SCHEMA"
    UI_SCHEMA = "UI_SCHEMA"
    VALIDATE = "VALIDATE"
    AUTH_EVALUATE = "AUTH_EVALUATE"
    AUTH_CONFIGURATION_GET = "AUTH_CONFIGURATION_GET"
    AUTH_CONFIGURATION_PUT = "AUTH_CONFIGURATION_PUT"
    AUTH_ROLES = "AUTH_ROLES"
    DELETE = "DELETE"

    # Versioning only
    VERSION = "VERSION"

    # Lock management
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    LOCK_HISTORY = "LOCK_HISTORY"
    LOCKED = "LOCKED"

    # These are special proxy routes which enable the username to be specified -
    # need to be protected by special role protections - currently only used for
    # datasets through the data store API
    PROXY_SEED = "PROXY_SEED"
    PROXY_CREATE = "PROXY_CREATE"
    PROXY_UPDATE = "PROXY_UPDATE"
    PROXY_REVERT = "PROXY_REVERT"
    # Versioning only
    PROXY_VERSION = "PROXY_VERSION"

    # Proxy fetch is only accessible via either prov/data store service accounts
    # and accepts a username to use for checking authorisation
    PROXY_FETCH = "PROXY_FETCH"



STANDARD_ROUTE_ACTIONS: List[RouteActions] = [
    RouteActions.SEED,
    RouteActions.UPDATE,
    RouteActions.CREATE,
    RouteActions.REVERT,
    RouteActions.DELETE,
    RouteActions.FETCH,
    # all item types may need to be proxy fetched
    RouteActions.PROXY_FETCH,
    RouteActions.LIST,
    RouteActions.SCHEMA,
    RouteActions.UI_SCHEMA,
    RouteActions.VALIDATE,
    RouteActions.AUTH_EVALUATE,
    RouteActions.AUTH_CONFIGURATION_GET,
    RouteActions.AUTH_CONFIGURATION_PUT,
    RouteActions.AUTH_ROLES,
    RouteActions.LOCK,
    RouteActions.UNLOCK,
    RouteActions.LOCK_HISTORY,
    RouteActions.LOCKED,
]