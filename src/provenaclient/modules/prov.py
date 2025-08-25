'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Friday November 29th 2024 4:21:39 pm +1000
Modified By: Parth Kulkarni
-----
Description: Provenance API L3 module. Includes the ProvAPI sub module. Contains IO helper functions for writing/reading files.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

29-11-2024 | Parth Kulkarni | Added generate-report functionality. 
22-08-2025 | Peter Baker | Added delete model run capability

'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import ProvClient, RegistryClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from provenaclient.utils.helpers import read_file_helper, write_file_helper, get_and_validate_file_path
from typing import List
from provenaclient.models.general import CustomLineageResponse, HealthCheckResponse
from ProvenaInterfaces.ProvenanceAPI import LineageResponse, ModelRunRecord, ConvertModelRunsResponse, RegisterModelRunResponse, RegisterBatchModelRunRequest, RegisterBatchModelRunResponse, PostUpdateModelRunResponse, GenerateReportRequest, PostDeleteGraphResponse
from ProvenaInterfaces.RegistryAPI import ItemModelRun, ItemSubType
from ProvenaInterfaces.SharedTypes import StatusResponse

# L3 interface.

PROV_API_DEFAULT_SEARCH_DEPTH = 3
DEFAULT_CONFIG_FILE_NAME = "prov-api.env"
DEFAULT_RELATIVE_FILE_PATH = "./"


class ProvAPIAdminSubModule(ModuleService):
    _prov_api_client: ProvClient
    _registry_api_client: RegistryClient

    def __init__(self, auth: AuthManager, config: Config, prov_api_client: ProvClient, registry_api_client: RegistryClient) -> None:
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

        # Clients related to the prov_api scoped as private.
        self._prov_api_client = prov_api_client
        self._registry_api_client = registry_api_client

    async def generate_config_file(self, required_only: bool = True, file_path: Optional[str] = None, write_to_file: bool = False) -> str:
        """Generates a nicely formatted .env file of the current required/non supplied properties 
        Used to quickly bootstrap a local environment or to understand currently deployed API.

        Parameters
        ----------
        required_only : bool, optional
            By default True
        file_path: str, optional
            The path you want to save the config file at WITH the file name. If you don't specify a path
            this will be saved in a relative directory.
        write_to_file: bool, By default False
            A boolean flag to indicate whether you want to save the config response to a file
            or not.

        Returns
        ----------
        str: Response containing the config text.

        """

        file_path = get_and_validate_file_path(
            file_path=file_path, write_to_file=write_to_file, default_file_name=DEFAULT_CONFIG_FILE_NAME)

        config_text: str = await self._prov_api_client.admin.generate_config_file(required_only=required_only)

        if config_text is None:
            raise ValueError(
                f"No data returned for generate config file endpoint.")

        # Write to file if config text is not None, write to file is True and file path is not None.
        if write_to_file:
            if file_path is None:
                raise ValueError("File path is not set for writing the CSV.")
            write_file_helper(file_path=file_path, content=config_text)

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

        return await self._prov_api_client.admin.store_record(registry_record=registry_record, validate_record=validate_record)

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

        return await self._prov_api_client.admin.store_multiple_records(registry_record=registry_record, validate_record=validate_record)

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

    async def delete_model_run_provenance(self, model_run_id: str, trial_mode: bool = False) -> PostDeleteGraphResponse:
        """Deletes a model run by its ID - provenance store ONLY"""
        return await self._prov_api_client.admin.delete_model_run_provenance(model_run_id=model_run_id, trial_mode=trial_mode)

    async def delete_model_run_provenance_and_registry(self, model_run_id: str, trial_mode: bool = False) -> PostDeleteGraphResponse:
        """Deletes a model run by its ID in both the registry AND in the provenance store."""
        # First, delete from provenance
        diff = await self._prov_api_client.admin.delete_model_run_provenance(model_run_id=model_run_id, trial_mode=trial_mode)

        if (trial_mode):
            # done if we are in trial mode - do not execute action
            return diff

        else:
            await self._registry_api_client.admin.delete_item(id=model_run_id, item_subtype=ItemSubType.MODEL_RUN)
            return diff


class Prov(ModuleService):
    _prov_client: ProvClient

    def __init__(self, auth: AuthManager, config: Config, prov_client: ProvClient, registry_client: RegistryClient) -> None:
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
        self.admin = ProvAPIAdminSubModule(
            auth, config, prov_client, registry_client)

    async def get_health_check(self) -> HealthCheckResponse:
        """Checks the health status of the PROV-API.

        Returns
        -------
        HealthCheckResponse
            Response containing the PROV-API health information.
        """

        return await self._prov_api_client.get_health_check()

    async def update_model_run(self, model_run_id: str, reason: str, record: ModelRunRecord) -> PostUpdateModelRunResponse:
        """Updates an existing model run with new information.

        This function triggers an asynchronous update of a model run. The update is processed as a job,
        and the job session ID is returned for tracking the update progress.

        Args:
            model_run_id (str): The ID of the model run to update
            reason (str): The reason for updating the model run 
            record (ModelRunRecord): The new model run record details

        Returns:
            PostUpdateModelRunResponse: Response containing the job session ID tracking the update

        Example:
            ```python
            response = await prov_api.update_model_run(
                model_run_id="10378.1/1234567",
                reason="Updating input dataset information",
                record=updated_model_run_record
            )
            # Get the session ID to track progress
            session_id = response.session_id
            ```
        """
        return await self._prov_api_client.post_update_model_run(
            model_run_id=model_run_id,
            reason=reason,
            record=record
        )

    async def explore_upstream(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> CustomLineageResponse:
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
        CustomLineageResponse
            A typed response containing the status, node count, and networkx serialised graph response.
        """

        upstream_response = await self._prov_api_client.explore_upstream(starting_id=starting_id, depth=depth)
        typed_upstream_response = CustomLineageResponse.parse_obj(
            upstream_response.dict())
        return typed_upstream_response

    async def explore_downstream(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> CustomLineageResponse:
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
        CustomLineageResponse
            A typed response containing the status, node count, and networkx serialised graph response.
        """

        typed_downstream_response = await self._prov_api_client.explore_downstream(starting_id=starting_id, depth=depth)
        typed_downstream_response = CustomLineageResponse.parse_obj(
            typed_downstream_response.dict())
        return typed_downstream_response

    async def get_contributing_datasets(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> CustomLineageResponse:
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
        CustomLineageResponse
            A typed response containing the status, node count, and networkx serialised graph response.
        """

        contributing_datasets = await self._prov_api_client.get_contributing_datasets(starting_id=starting_id, depth=depth)
        typed_contributing_datasets = CustomLineageResponse.parse_obj(
            contributing_datasets.dict())
        return typed_contributing_datasets

    async def get_effected_datasets(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> CustomLineageResponse:
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
        CustomLineageResponse
            A typed response containing the status, node count, and networkx serialised graph response.
        """

        effected_datasets_response = await self._prov_api_client.get_effected_datasets(starting_id=starting_id, depth=depth)
        typed_effected_datasets = CustomLineageResponse.parse_obj(
            effected_datasets_response.dict())
        return typed_effected_datasets

    async def get_contributing_agents(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> CustomLineageResponse:
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
        CustomLineageResponse
            A typed response containing the status, node count, and networkx serialised graph response.
        """

        contributing_agents_response = await self._prov_api_client.get_contributing_agents(starting_id=starting_id, depth=depth)
        typed_contributing_agents = CustomLineageResponse.parse_obj(
            contributing_agents_response.dict())
        return typed_contributing_agents

    async def get_effected_agents(self, starting_id: str, depth: int = PROV_API_DEFAULT_SEARCH_DEPTH) -> CustomLineageResponse:
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
        CustomLineageResponse
            A typed response containing the status, node count, and networkx serialised graph response.
        """

        effected_agents_response = await self._prov_api_client.get_effected_agents(starting_id=starting_id, depth=depth)
        typed_effected_agents = CustomLineageResponse.parse_obj(
            effected_agents_response.dict())
        return typed_effected_agents

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

        return await self._prov_api_client.register_batch_model_runs(model_run_batch_payload=batch_model_run_payload)

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

    async def generate_csv_template(self, workflow_template_id: str, file_path: Optional[str] = None, write_to_csv: bool = False) -> str:
        """Generates a model run csv template to be utilised 
        for creating model runs through csv format..

        Parameters
        ----------
        workflow_template_id : str
            An ID of a created and existing model run workflow template.
        path_to_save_csv: str, optional 
            The path you want to save the csv file at WITH csv file name. If you don't specify a path
            this will be saved in a relative directory.
        write_to_csv: bool, By default False
            A boolean flag to indicate whether you want to save the template to a csv file
            or not.

        Returns
        ----------
        str: Response containing the csv template text (encoded in a csv format). 

        """

        file_path = get_and_validate_file_path(
            file_path=file_path, write_to_file=write_to_csv, default_file_name=workflow_template_id + ".csv")

        csv_text = await self._prov_api_client.generate_csv_template(workflow_template_id=workflow_template_id)

        if csv_text is None:
            raise ValueError(
                f"No data returned for generate CSV template workflow template ID {workflow_template_id}")

        # Write to file if CSV content is returned and write_to_csv is True and file path is assigned.
        if write_to_csv:
            if file_path is None:
                raise ValueError("File path is not set for writing the CSV.")
            write_file_helper(file_path=file_path, content=csv_text)

        return csv_text

    async def convert_model_runs(self, model_run_content: str) -> ConvertModelRunsResponse:
        """Converts model run with model_run_content provided as a string.

        Parameters
        ----------
        model_run_content : str
            The model run information containing
            the necessary parameters for model run lodge.

        Returns
        -------
        ConvertModelRunsResponse
            Returns the model run information in an interactive python
            datatype.

        Raises
        ------
        Exception
            Exception raised when converting string to bytes.
        """

        response = await self._prov_api_client.convert_model_runs_to_csv(csv_file_contents=model_run_content)

        return response

    async def convert_model_runs_to_csv_with_file(self, file_path: str) -> ConvertModelRunsResponse:
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

        file_content = read_file_helper(file_path=file_path)

        response = await self._prov_api_client.convert_model_runs_to_csv(csv_file_contents=file_content)
        return response

    async def regenerate_csv_from_model_run_batch(self, batch_id: str, file_path: Optional[str] = None, write_to_csv: bool = False) -> str:
        """Regenerate/create a csv file containing model 
        run information from a model run batch job.

        The batch id must exist in the system.

        Parameters
        ----------
        batch_id : str
            Obtained from creating a batch model run.
        file_path: str, optional 
            The path you want to save the csv file at WITH CSV file name. If you don't specify a path
            this will be saved in a relative directory.
        write_to_csv: bool, By default False
            A boolean flag to indicate whether you want to save the template to a csv file
            or not.

        Returns
        ----------
        str: Response containing the model run information (encoded in csv format).

        """

        file_path = get_and_validate_file_path(
            file_path=file_path, write_to_file=write_to_csv, default_file_name=batch_id + ".csv")

        csv_text: str = await self._prov_api_client.regenerate_csv_from_model_run_batch(batch_id=batch_id)

        if csv_text is None:
            raise ValueError(f"No data returned for batch ID {batch_id}")

        # Write to file if CSV content is returned and write_to_csv is True and file path is assigned.
        if write_to_csv:
            if file_path is None:
                raise ValueError("File path is not set for writing the CSV.")
            write_file_helper(file_path=file_path, content=csv_text)

        return csv_text

    async def generate_report(self, report_request: GenerateReportRequest, file_path: str = DEFAULT_RELATIVE_FILE_PATH) -> None:
        """Generates a provenance report from a Study or Model Run Entity containing the
        associated inputs, model runs and outputs involved. 

        The report is generated in `.docx` and saved at relative directory level.

        Parameters
        ----------
        report_request : GenerateReportRequest
            The request object containing the parameters for generating the report, including the `id`, 
            `item_subtype`, and `depth`.
        """
        # Calls API endpoint to generate report document.
        generated_word_file = await self._prov_api_client.generate_report(
            report_request=report_request
        )

        # Sanitize the id to avoid file system errors
        sanitized_filename = report_request.id.replace(
            "/", "_") + " - Study Close Out Report.docx"

        # Append file path and file-name together
        file_path = file_path + sanitized_filename

        # Writes content into word docx file.
        write_file_helper(file_path=file_path, content=generated_word_file)
