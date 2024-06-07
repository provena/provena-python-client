from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import ProvClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from provenaclient.utils.helpers import prepare_httpx_files_csv_request, write_file_helper
from typing import List
from provenaclient.models.general import HealthCheckResponse
from ProvenaInterfaces.ProvenanceAPI import LineageResponse, ModelRunRecord, ConvertModelRunsResponse, RegisterModelRunResponse, RegisterBatchModelRunRequest, RegisterBatchModelRunResponse
from ProvenaInterfaces.RegistryAPI import ItemModelRun
from ProvenaInterfaces.SharedTypes import StatusResponse

# L3 interface.

PROV_API_DEFAULT_SEARCH_DEPTH = 3
DEFAULT_CONFIG_FILE_NAME = "prov-api.env"


class ProvAPIAdminSubModule(ModuleService):
    _prov_api_client: ProvClient

    def __init__(self, auth: AuthManager, config: Config, prov_api_client: ProvClient) -> None:
        """
        Admin sub module of the Prov API providing functionality
        for the admin endpoints.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance. 
        auth_client: AuthClient
            The instantiated auth client
        """
        self._auth = auth
        self._config = config

        # Clients related to the datastore scoped as private.
        self._prov_api_client = prov_api_client

    async def generate_config_file(self, path_to_save_file: Optional[str], required_only: bool = True, file_name: str = DEFAULT_CONFIG_FILE_NAME, write_to_file: bool = True) -> str:
        """Generates a nicely formatted .env file of the current required/non supplied properties 
        Used to quickly bootstrap a local environment or to understand currently deployed API.

        Parameters
        ----------
        required_only : bool, optional
            By default True
        file_name : str, optional
            The filename you want to have, by default DEFAULT_CONFIG_FILE_NAME (prov-api.env)
        path_to_save_file: str, optional
            The path you want to save the config file at. If you don't specify a path
            this will be saved in a relative directory.
        write_to_file: bool, By default True
            A boolean flag to indicate whether you want to save the config response to a file
            or not.

        Returns
        ----------
        str: Response containing the config text.

        """

        config_text: str = await self._prov_api_client.admin.generate_config_file(required_only=required_only)

        if config_text and write_to_file:
            write_file_helper(file_name=file_name, path_to_save_at=path_to_save_file, content=config_text)

        return config_text
    
    async def store_record(self, registry_record: ItemModelRun, validate_record: bool = True) -> StatusResponse:
        """An admin only endpoint which enables the reupload/storage of an existing completed provenance record.

        Parameters
        ----------
        registry_record : ItemModelRun
            The completed registry record for the model run.
        validate_record: bool
            Optional Should the ids in the payload be validated?, by default True

        Returns
        -------
        StatusResponse
            A status response indicating the success of the request and any other details.
        """

        return await self._prov_api_client.admin.store_record(registry_record=registry_record, validate_record = validate_record)
        
    async def store_multiple_records(self, registry_record: List[ItemModelRun], validate_record: bool = True) -> StatusResponse:
        """An admin only endpoint which enables the reupload/storage of an existing but multiple completed provenance record.

        Parameters
        ----------
        registry_record : List[ItemModelRun]
            List of the completed registry record for the model run validate_record
        validate_record: bool
            Optional Should the ids in the payload be validated?, by default True

        Returns
        -------
        StatusResponse
            A status response indicating the success of the request and any other details.
        """

        return await self._prov_api_client.admin.store_multiple_records(registry_record=registry_record, validate_record = validate_record)

    async def store_all_registry_records(self, validate_record: bool = True) -> StatusResponse:
        """Applies the store record endpoint action across a list of ItemModelRuns '
           which is found by querying the registry model run list endpoint directly.

        Parameters
        ----------
        validate_record : bool
            Optional Should the ids in the payload be validated?, by default True


        Returns
        -------
        StatusResponse
            A status response indicating the success of the request and any other details.
        """

        return await self._prov_api_client.admin.store_all_registry_records(validate_record=validate_record)



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

        # Submodules 
        self.admin = ProvAPIAdminSubModule(auth, config, prov_client)
    
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

        Note: You can utilise the returned session ID to poll on 
        the JOB API to check status of the model run registration(s).

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

        Note: You can utilise the returned session ID to poll on 
        the JOB API to check status of the model run registration.

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
    
    async def generate_csv_template(self, workflow_template_id: str, path_to_save_csv: Optional[str] = None, write_to_csv: bool = True) -> str:
        """Generates a model run csv template to be utilised 
        for creating model runs through csv format..

        Parameters
        ----------
        workflow_template_id : str
            An ID of a created and existing model run workflow template.
        path_to_save_csv: str, optional 
            The path you want to save the csv file at. If you don't specify a path
            this will be saved in a relative directory.
        write_to_csv: bool, By default True
            A boolean flag to indicate whether you want to save the template to a csv file
            or not.

        Returns
        ----------
        str: Response containing the csv template text (encoded in a csv format). 
        
        """

        csv_text = await self._prov_api_client.generate_csv_template(workflow_template_id=workflow_template_id)

        if csv_text and write_to_csv:
            write_file_helper(file_name=f"WorkflowTemplate-{workflow_template_id}.csv", path_to_save_at=path_to_save_csv, content = csv_text)

        return csv_text

    async def convert_model_runs_to_csv(self, file_path: str) -> ConvertModelRunsResponse:
        """Reads a CSV file, and it's defined model run contents
        and lodges a model run.

        Parameters
        ----------
        file_path : str
            The path of an existing created CSV file containing
            the necessary parameters for model run lodge.

        Returns
        -------
        ConvertModelRunsResponse
            Returns the model run information in an interactive python
            datatype.

        """

        files = prepare_httpx_files_csv_request(file_path = file_path)

        response = await self._prov_api_client.convert_model_runs_to_csv(csv_file=files)
        return response

    async def regenerate_csv_from_model_run_batch(self, batch_id: str, path_to_save_csv: Optional[str] = None, write_to_csv: bool = True) -> str:
        """Regenerate/create a csv file containing model 
        run information from a model run batch job.

        The batch id must exist in the system.

        Parameters
        ----------
        batch_id : str
            Obtained from creating a batch model run.
        path_to_save_csv: str, optional 
            The path you want to save the csv file at. If you don't specify a path
            this will be saved in a relative directory.
        write_to_csv: bool, By default True
            A boolean flag to indicate whether you want to save the template to a csv file
            or not.

        Returns
        ----------
        str: Response containing the model run information (encoded in csv format).
        
        """
        
        csv_text: str = await self._prov_api_client.regenerate_csv_from_model_run_batch(batch_id=batch_id)

        if csv_text and write_to_csv:
            write_file_helper(file_name=batch_id + ".csv", path_to_save_at=path_to_save_csv, content=csv_text)

        return csv_text