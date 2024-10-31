'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: Prov API L2 Client.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Note that this layer does not provide any file IO capabilities - see L3
'''

from typing import List, cast
from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from provenaclient.models.general import HealthCheckResponse
from ProvenaInterfaces.ProvenanceAPI import LineageResponse, ModelRunRecord, RegisterModelRunResponse, RegisterBatchModelRunRequest, RegisterBatchModelRunResponse, ConvertModelRunsResponse, PostUpdateModelRunResponse, PostUpdateModelRunInput
from ProvenaInterfaces.RegistryAPI import ItemModelRun


class ProvAPIEndpoints(str, Enum):
    """An ENUM containing the prov api endpoints."""

    # Completed
    POST_MODEL_RUN_REGISTER = "/model_run/register"
    POST_MODEL_RUN_UPDATE = "/model_run/update"
    POST_MODEL_RUN_REGISTER_BATCH = "/model_run/register_batch"
    GET_EXPLORE_UPSTREAM = "/explore/upstream"
    GET_EXPLORE_DOWNSTREAM = "/explore/downstream"
    GET_EXPLORE_SPECIAL_CONTRIBUTING_DATASETS = "/explore/special/contributing_datasets"
    GET_EXPLORE_SPECIAL_EFFECTED_DATASETS = "/explore/special/effected_datasets"
    GET_EXPLORE_SPECIAL_CONTRIBUTING_AGENTS = "/explore/special/contributing_agents"
    GET_EXPLORE_SPECIAL_EFFECTED_AGENTS = "/explore/special/effected_agents"
    GET_HEALTH_CHECK = "/"
    GET_BULK_GENERATE_TEMPLATE_CSV = "/bulk/generate_template/csv"
    POST_BULK_CONVERT_MODEL_RUNS_CSV = "/bulk/convert_model_runs/csv"
    GET_BULK_REGENERATE_FROM_BATCH_CSV = "/bulk/regenerate_from_batch/csv"

    # Not completed.
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"


class ProvAPIAdminEndpoints(str, Enum):
    """An ENUM containing the prov api admin endpoints."""

    # Completed
    GET_ADMIN_CONFIG = "/admin/config"
    POST_ADMIN_STORE_RECORD = "/admin/store_record"
    POST_ADMIN_STORE_RECORDS = "/admin/store_records"
    POST_ADMIN_STORE_ALL_REGISTRY_RECORDS = "/admin/store_all_registry_records"

    # Not completed yet, TODO.
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"


# L2 interface.


class ProvAdminClient(ClientService):

    def __init__(self, auth: AuthManager, config: Config) -> None:
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: ProvAPIAdminEndpoints) -> str:
        return self._config.prov_api_endpoint + endpoint.value

    async def generate_config_file(self, required_only: bool) -> str:
        """Generates a nicely formatted .env file of the current required/non supplied properties 
        Used to quickly bootstrap a local environment or to understand currently deployed API.

        Parameters
        ----------
        required_only : bool, optional
            By default True
        """

        response = await validated_get_request(
            client=self,
            url=self._build_endpoint(ProvAPIAdminEndpoints.GET_ADMIN_CONFIG),
            error_message=f"Failed to generate config file",
            params={"required_only": required_only},
        )

        return response.text

    async def store_record(self, registry_record: ItemModelRun, validate_record: bool) -> StatusResponse:
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

        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                ProvAPIAdminEndpoints.POST_ADMIN_STORE_RECORD),
            error_message=f"Failed to store record with display name {registry_record.display_name} and id {registry_record.id}",
            params={"validate_record": validate_record},
            json_body=py_to_dict(registry_record),
            model=StatusResponse
        )

    async def store_multiple_records(self, registry_record: List[ItemModelRun], validate_record: bool) -> StatusResponse:
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

        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                ProvAPIAdminEndpoints.POST_ADMIN_STORE_RECORDS),
            error_message=f"Failed to complete multiple store record request.",
            params={"validate_record": validate_record},
            model=StatusResponse,
            json_body=cast(List[Dict[str, Any]], [py_to_dict(item)
                           for item in registry_record])
        )

    async def store_all_registry_records(self, validate_record: bool) -> StatusResponse:
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

        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                ProvAPIAdminEndpoints.POST_ADMIN_STORE_ALL_REGISTRY_RECORDS),
            error_message=f"Failed to validate records.",
            params={"validate_record": validate_record},
            json_body=None,
            model=StatusResponse
        )


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

    async def post_update_model_run(self, model_run_id: str, reason: str, record: ModelRunRecord) -> PostUpdateModelRunResponse:
        """Updates an existing model run in the system.

        Args:
            model_run_id (str): The ID of the model run to update
            reason (str): The reason for the update
            record (ModelRunRecord): The updated model run record

        Returns:
            PostUpdateModelRunResponse: The response containing the job session ID
        """
        update_payload = PostUpdateModelRunInput(
            model_run_id=model_run_id,
            reason=reason,
            record=record
        )

        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(ProvAPIEndpoints.POST_MODEL_RUN_UPDATE),
            error_message=f"Model run update failed for ID {model_run_id}!",
            params={},
            json_body=py_to_dict(update_payload),
            model=PostUpdateModelRunResponse
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
            url=self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_UPSTREAM),
            error_message=f"Upstream query with starting id {starting_id} and depth {depth} failed!",
            params={"starting_id": starting_id, "depth": depth},
            model=LineageResponse
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
            url=self._build_endpoint(ProvAPIEndpoints.GET_EXPLORE_DOWNSTREAM),
            error_message=f"Downstream query with starting id {starting_id} and depth {depth} failed!",
            params={"starting_id": starting_id, "depth": depth},
            model=LineageResponse
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
            url=self._build_endpoint(
                ProvAPIEndpoints.GET_EXPLORE_SPECIAL_CONTRIBUTING_DATASETS),
            error_message=f"Contributing datasets query with starting id {starting_id} and depth {depth} failed!",
            params={"starting_id": starting_id, "depth": depth},
            model=LineageResponse
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
            url=self._build_endpoint(
                ProvAPIEndpoints.GET_EXPLORE_SPECIAL_EFFECTED_DATASETS),
            error_message=f"Effected datasets query with starting id {starting_id} and depth {depth} failed!",
            params={"starting_id": starting_id, "depth": depth},
            model=LineageResponse
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
            url=self._build_endpoint(
                ProvAPIEndpoints.GET_EXPLORE_SPECIAL_CONTRIBUTING_AGENTS),
            error_message=f"Contributing agents query with starting id {starting_id} and depth {depth} failed!",
            params={"starting_id": starting_id, "depth": depth},
            model=LineageResponse
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
            url=self._build_endpoint(
                ProvAPIEndpoints.GET_EXPLORE_SPECIAL_EFFECTED_AGENTS),
            error_message=f"Effected agents query with starting id {starting_id} and depth {depth} failed!",
            params={"starting_id": starting_id, "depth": depth},
            model=LineageResponse
        )

    # Model run endpoints.

    async def register_batch_model_runs(self, model_run_batch_payload: RegisterBatchModelRunRequest) -> RegisterBatchModelRunResponse:
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

        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(
                ProvAPIEndpoints.POST_MODEL_RUN_REGISTER_BATCH),
            error_message=f"Model run batch registration failed!",
            params={},
            json_body=py_to_dict(model_run_batch_payload),
            model=RegisterBatchModelRunResponse
        )

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

        return await parsed_post_request(
            client=self,
            url=self._build_endpoint(ProvAPIEndpoints.POST_MODEL_RUN_REGISTER),
            error_message=f"Model run registration failed!",
            params={},
            json_body=py_to_dict(model_run_payload),
            model=RegisterModelRunResponse
        )

    # CSV template tools endpoints

    async def generate_csv_template(self, workflow_template_id: str) -> str:
        """Generates a model run csv template to be utilised 
        for creating model runs through csv format.

        Parameters
        ----------
        workflow_template_id : str
            An ID of a created and existing model run workflow template.
        """

        response = await validated_get_request(
            client=self,
            url=self._build_endpoint(
                ProvAPIEndpoints.GET_BULK_GENERATE_TEMPLATE_CSV),
            error_message=f"Failed to generate CSV file",
            params={"workflow_template_id": workflow_template_id},
        )

        return response.text

    async def convert_model_runs_to_csv(self, csv_file_contents: str) -> ConvertModelRunsResponse:
        """Reads a CSV file, and it's defined model run contents
        and lodges a model run.

        Parameters
        ----------
        csv_file_contents : str
            Contains the model run contents.

        Returns
        -------
        ConvertModelRunsResponse
            Returns the model run information in an interactive python
            datatype.
        """

        # Convert string to bytes.
        try:
            model_run_content_encoded: ByteString = csv_file_contents.encode(
                "utf-8")
        except Exception as e:
            raise Exception(
                f"Exception has occurred while encoding model run content: {e}")

        # The csv file object to be used for httpx post requests
        # A dictionary representing file(s) to be uploaded with the
        # request. Each key in the dictionary is the name of the form field for the file according,
        # to API specifications. For Provena it's "csv_file" and and the value
        # is a tuple of (filename, filedata, MIME type / media type).
        csv_file: HttpxFileUpload = {"csv_file": (
            "upload.csv", model_run_content_encoded, "text/csv")}

        return await parsed_post_request_with_status(
            client=self,
            url=self._build_endpoint(
                ProvAPIEndpoints.POST_BULK_CONVERT_MODEL_RUNS_CSV),
            error_message="Failed to generate CSV file",
            files=csv_file,
            json_body=None,
            params={},
            model=ConvertModelRunsResponse
        )

    async def regenerate_csv_from_model_run_batch(self, batch_id: str) -> str:
        """Regenerate/create a csv file containing model 
        run information from a model run batch job.

        The batch id must exist in the system.

        Parameters
        ----------
        batch_id : str
            Obtained from creating a batch model run.
        """

        response = await validated_get_request(
            client=self,
            url=self._build_endpoint(
                ProvAPIEndpoints.GET_BULK_REGENERATE_FROM_BATCH_CSV),
            error_message=f"Failed to generate CSV file from batch_id {batch_id}",
            params={"batch_id": batch_id},
        )

        return response.text
