from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from provenaclient.models.general import HealthCheckResponse
from ProvenaInterfaces.ProvenanceAPI import LineageResponse, ModelRunRecord, RegisterModelRunResponse, RegisterBatchModelRunRequest, RegisterBatchModelRunResponse


class ProvAPIEndpoints(str, Enum):
    """An ENUM containing the prov api endpoints."""
    
    # Completed
    POST_MODEL_RUN_REGISTER = "/model_run/register"
    POST_MODEL_RUN_REGISTER_BATCH = "/model_run/register_batch"
    GET_EXPLORE_UPSTREAM = "/explore/upstream"
    GET_EXPLORE_DOWNSTREAM = "/explore/downstream"
    GET_EXPLORE_SPECIAL_CONTRIBUTING_DATASETS = "/explore/special/contributing_datasets"
    GET_EXPLORE_SPECIAL_EFFECTED_DATASETS = "/explore/special/effected_datasets"
    GET_EXPLORE_SPECIAL_CONTRIBUTING_AGENTS = "/explore/special/contributing_agents"
    GET_EXPLORE_SPECIAL_EFFECTED_AGENTS = "/explore/special/effected_agents"
    GET_HEALTH_CHECK = "/"

    
    
    # Not completed.
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    GET_BULK_GENERATE_TEMPLATE_CSV = "/bulk/generate_template/csv"
    POST_BULK_CONVERT_MODEL_RUNS_CSV = "/bulk/convert_model_runs/csv"
    GET_BULK_REGENERATE_FROM_BATCH_CSV = "/bulk/regenerate_from_batch/csv"

class ProvAPIAdminEndpoints(str, Enum):


    # Not completed yet, TODO.
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    POST_ADMIN_STORE_RECORD = "/admin/store_record"
    POST_ADMIN_STORE_RECORDS = "/admin/store_records"
    POST_ADMIN_STORE_ALL_REGISTRY_RECORDS = "/admin/store_all_registry_records"
    
#L2 interface.


class ProvAdminClient(ClientService):

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self._auth = auth
        self._config = config
    
    def _build_endpoint(self, endpoint: ProvAPIEndpoints) -> str:
       return self._config.prov_api_endpoint + endpoint.value
    
class ProvClient(ClientService):

    admin: ProvAdminClient

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the REPLACEClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

        self.admin = ProvAdminClient(auth=auth, config=config)

    def _build_endpoint(self, endpoint: ProvAPIEndpoints) -> str:
       return self._config.prov_api_endpoint + endpoint.value
    
    async def get_health_check(self) -> HealthCheckResponse:
        """Checks the health status of the PROV-API.

        Returns
        -------
        HealthCheckResponse
            Response containing the PROV-API health information.
        """

        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(ProvAPIEndpoints.GET_HEALTH_CHECK),
            error_message="Health check failed!",
            params={},
            model=HealthCheckResponse
        )
    
    # Explore Lineage endpoints
    async def explore_upstream(self, starting_id: str, depth: int) -> LineageResponse:
        """Explores in the upstream direction (inputs/associations) 
        starting at the specified node handle ID. 
        The search depth is bounded by the depth parameter which has a default maximum of 100.

        Parameters
        ----------
        starting_id : str
            The ID of the entity to start at.
        depth : int, optional
            The depth to traverse in the upstream direction, by default 100.

        Returns
        -------
        LineageResponse
            A response containing the status, node count, and networkx serialised graph response.
        """

        return await parsed_get_request_with_status(
            client=self, 
            url = self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_UPSTREAM),
            error_message=f"Upstream query with starting id {starting_id} and depth {depth} failed!",
            params = {"starting_id": starting_id, "depth": depth},
            model = LineageResponse
        )

 
    async def explore_downstream(self, starting_id: str, depth: int) -> LineageResponse:
        """Explores in the downstream direction (inputs/associations) 
        starting at the specified node handle ID. 
        The search depth is bounded by the depth parameter which has a default maximum of 100.

        Parameters
        ----------
        starting_id : str
            The ID of the entity to start at.
        depth : int, optional
            The depth to traverse in the downstream direction, by default 100

        Returns
        -------
        LineageResponse
            A response containing the status, node count, and networkx serialised graph response.
        """
        
        return await parsed_get_request_with_status(
            client=self, 
            url = self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_DOWNSTREAM),
            error_message=f"Downstream query with starting id {starting_id} and depth {depth} failed!",
            params = {"starting_id": starting_id, "depth": depth},
            model = LineageResponse
        )
    
    async def get_contributing_datasets(self, starting_id: str, depth: int) -> LineageResponse:
        """Fetches datasets (inputs) which involved in a model run
        naturally in the upstream direction.

        Parameters
        ----------
        starting_id : str
            The ID of the entity to start at.
        depth : int, optional
            The depth to traverse in the upstream direction, by default 100

        Returns
        -------
        LineageResponse
            A response containing the status, node count, and networkx serialised graph response.
        """

        return await parsed_get_request_with_status(
            client=self, 
            url = self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_SPECIAL_CONTRIBUTING_DATASETS),
            error_message=f"Contributing datasets query with starting id {starting_id} and depth {depth} failed!",
            params = {"starting_id": starting_id, "depth": depth},
            model = LineageResponse
        )
    
    async def get_effected_datasets(self, starting_id: str, depth: int) -> LineageResponse:
        """Fetches datasets (outputs) which are derived from the model run
        naturally in the downstream direction.

        Parameters
        ----------
        starting_id : str
            The ID of the entity to start at.
        depth : int, optional
            The depth to traverse in the downstream direction, by default 100.

        Returns
        -------
        LineageResponse
            A response containing the status, node count, and networkx serialised graph response.
        """

        return await parsed_get_request_with_status(
            client=self, 
            url = self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_SPECIAL_EFFECTED_DATASETS),
            error_message=f"Effected datasets query with starting id {starting_id} and depth {depth} failed!",
            params = {"starting_id": starting_id, "depth": depth},
            model = LineageResponse
        )
    
    async def get_contributing_agents(self, starting_id: str, depth: int) -> LineageResponse:
        """Fetches agents (organisations or peoples) that are involved or impacted by the model run.
        naturally in the upstream direction.

        Parameters
        ----------
        starting_id : str
            The ID of the entity to start at.
        depth : int, optional
            The depth to traverse in the upstream direction, by default 100.

        Returns
        -------
        LineageResponse
            A response containing the status, node count, and networkx serialised graph response.
        """

        return await parsed_get_request_with_status(
            client=self, 
            url = self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_SPECIAL_CONTRIBUTING_AGENTS),
            error_message=f"Contributing agents query with starting id {starting_id} and depth {depth} failed!",
            params = {"starting_id": starting_id, "depth": depth},
            model = LineageResponse
        )
    
    async def get_effected_agents(self, starting_id: str, depth: int) -> LineageResponse:
        """Fetches agents (organisations or peoples) that are involved or impacted by the model run.
        naturally in the downstream direction.

        Parameters
        ----------
        starting_id : str
            The ID of the entity to start at.
        depth : int, optional
            The depth to traverse in the downstream direction, by default 100.

        Returns
        -------
        LineageResponse
            A response containing the status, node count, and networkx serialised graph response.
        """

        return await parsed_get_request_with_status(
            client=self, 
            url = self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_SPECIAL_EFFECTED_AGENTS),
            error_message=f"Effected agents query with starting id {starting_id} and depth {depth} failed!",
            params = {"starting_id": starting_id, "depth": depth},
            model = LineageResponse
        )
    

    # Model run endpoints.

    async def register_batch_model_runs(self, model_run_batch_payload:RegisterBatchModelRunRequest) -> RegisterBatchModelRunResponse:
        """This function allows you to register multiple model runs in one go (batch) asynchronously.

        Parameters
        ----------
        batch_model_run_payload : RegisterBatchModelRunRequest
            A list of model runs (ModelRunRecord objects)

        Returns
        -------
        RegisterBatchModelRunResponse
            The job session id derived from job-api for the model-run batch. 
        """

        return await parsed_post_request(
            client = self, 
            url = self._build_endpoint(ProvAPIEndpoints.POST_MODEL_RUN_REGISTER_BATCH),
            error_message=f"Model run batch registration failed!",
            params = {},
            json_body=py_to_dict(model_run_batch_payload),
            model = RegisterBatchModelRunResponse
        )    

    async def register_model_run(self, model_run_payload: ModelRunRecord) -> RegisterModelRunResponse:
        """Asynchronously registers a single model run.

        Parameters
        ----------
        model_run_payload : ModelRunRecord
            Contains information needed for the 
            model run such as workflow template,
            inputs, outputs, description etc. 

        Returns
        -------
        RegisterModelRunResponse
            The job session id derived from job-api for the model-run. 
        """

        return await parsed_post_request(
            client = self, 
            url = self._build_endpoint(ProvAPIEndpoints.POST_MODEL_RUN_REGISTER), 
            error_message=f"Model run registration failed!", 
            params = {},
            json_body=py_to_dict(model_run_payload),
            model = RegisterModelRunResponse
        )
    

    # CSV template tools endpoints
    #async def generate_csv_template(self, workflow_template_id: str) -> None: 
    #async def convert_model_runs_to_csv(self) -> None:


        
