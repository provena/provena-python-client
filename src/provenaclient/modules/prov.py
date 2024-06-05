from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import ProvClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from typing import List
from provenaclient.models.general import HealthCheckResponse
from ProvenaInterfaces.ProvenanceAPI import LineageResponse, ModelRunRecord, RegisterModelRunResponse, RegisterBatchModelRunRequest, RegisterBatchModelRunResponse


# L3 interface.

PROV_API_DEFAULT_SEARCH_DEPTH = 100

class Prov(ModuleService):
    _prov_client: ProvClient

    def __init__(self, auth: AuthManager, config: Config, prov_client: ProvClient) -> None:
        """Initialises a new datastore object, which sits between the user and the datastore api operations.

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

        # Clients related to the prov-api scoped as private.
        self._prov_api_client = prov_client

    
    async def get_health_check(self) -> HealthCheckResponse:
        """Checks the health status of the PROV-API.

        Returns
        -------
        HealthCheckResponse
            Response containing the PROV-API health information.
        """

        return await self._prov_api_client.get_health_check()

    async def explore_upstream(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> LineageResponse:
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

        return await self._prov_api_client.explore_upstream(starting_id=starting_id, depth=depth) 
    
    async def explore_downstream(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> LineageResponse:
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

        return await self._prov_api_client.explore_downstream(starting_id=starting_id, depth=depth)
    
    async def get_contributing_datasets(self, starting_id: str, depth:int = PROV_API_DEFAULT_SEARCH_DEPTH) -> LineageResponse:
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

        return await self._prov_api_client.get_contributing_datasets(starting_id=starting_id, depth=depth)
    
    async def get_effected_datasets(self, starting_id: str, depth:int = PROV_API_DEFAULT_SEARCH_DEPTH) -> LineageResponse:
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

        return await self._prov_api_client.get_effected_datasets(starting_id=starting_id, depth=depth)

    async def get_contributing_agents(self, starting_id: str, depth:int = PROV_API_DEFAULT_SEARCH_DEPTH) -> LineageResponse:
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

        return await self._prov_api_client.get_contributing_agents(starting_id=starting_id, depth=depth)

    async def get_effected_agents(self, starting_id: str, depth:int = PROV_API_DEFAULT_SEARCH_DEPTH) -> LineageResponse:
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

        return await self._prov_api_client.get_effected_agents(starting_id=starting_id, depth=depth)

    async def register_batch_model_runs(self, batch_model_run_payload: RegisterBatchModelRunRequest) -> RegisterBatchModelRunResponse:
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

        return await self._prov_api_client.register_batch_model_runs(model_run_batch_payload = batch_model_run_payload)

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

        return await self._prov_api_client.register_model_run(model_run_payload=model_run_payload)