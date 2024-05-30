from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
from enum import Enum 
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *

class JobAPIEndpoints(str, Enum):
    """An ENUM containing the job api endpoints."""
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    GET_JOBS_USER_FETCH = "/jobs/user/fetch"
    POST_JOBS_USER_LIST = "/jobs/user/list"
    POST_JOBS_USER_LIST_BATCH = "/jobs/user/list_batch"
    POST_JOBS_ADMIN_LAUNCH = "/jobs/admin/launch"
    GET_JOBS_ADMIN_FETCH = "/jobs/admin/fetch"
    POST_JOBS_ADMIN_LIST = "/jobs/admin/list"
    POST_JOBS_ADMIN_LIST_BATCH = "/jobs/admin/list_batch"
    GET_HEALTH_CHECK = "/"

# L2 interface.

class JobAPIClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the JobAPIClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: JobAPIEndpoints) -> str:
        return self._config.jobs_service_api_endpoint + endpoint.value
