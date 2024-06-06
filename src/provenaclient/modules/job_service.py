from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import JobAPIClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from provenaclient.models import HealthCheckResponse
from ProvenaInterfaces.AsyncJobAPI import *
from typing import List

# L3 interface.


class JobAdminSubService(ModuleService):
    _job_api_client: JobAPIClient

    def __init__(self, auth: AuthManager, config: Config, job_api_client: JobAPIClient) -> None:
        """Initialises a new job admin sub-service object, which sits between the user and the job-service api operations.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance. 
        job_api_client : JobAPIClient
            This client interacts with the Job API
        """
        self._auth = auth
        self._config = config

        # Clients related to the job-api scoped as private.
        self._job_api_client = job_api_client

    async def launch_job(self, request: AdminLaunchJobRequest) -> AdminLaunchJobResponse:
        """
        Launches a new job.

        Args:
            request (AdminLaunchJobRequest): Specified job parameters

        Returns:
            AdminLaunchJobResponse: The response
        """
        return await self._job_api_client.admin.launch_job(request=request)

    async def get_job(self, session_id: str) -> AdminGetJobResponse:
        """
        Fetches a job (any job since admin)

        Args:
            session_id (str): The session ID of job to fetch

        Returns:
            AdminGetJobResponse: The response
        """
        return await self._job_api_client.admin.get_job(session_id=session_id)

    async def list_jobs(self, list_jobs_request: AdminListJobsRequest) -> AdminListJobsResponse:
        """
        Lists all jobs.

        Args:
            list_jobs_request (AdminListJobsRequest): The request including pagination information.

        Returns:
            AdminListJobsResponse: The list of jobs response.
        """
        return await self._job_api_client.admin.list_jobs(list_jobs_request=list_jobs_request)

    async def list_job_batch(self, list_request: AdminListByBatchRequest) -> AdminListByBatchResponse:
        """
        List jobs by batch ID, returning a list of jobs in the batch.

        Args:
            list_request (AdminListByBatchRequest): The request including batch ID

        Returns:
            AdminListByBatchResponse: The list of jobs in the batch
        """
        return await self._job_api_client.admin.list_jobs_in_batch(list_request=list_request)


class JobService(ModuleService):
    _job_api_client: JobAPIClient

    admin: JobAdminSubService

    def __init__(self, auth: AuthManager, config: Config, job_api_client: JobAPIClient) -> None:
        """Initialises a new job-service object, which sits between the user and the job-service api operations.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance. 
        job_api_client : JobAPIClient
            This client interacts with the Job API
        """
        self._auth = auth
        self._config = config

        # Clients related to the job-api scoped as private.
        self._job_api_client = job_api_client

        # Sub modules
        self.admin = JobAdminSubService(
            auth=auth, config=config, job_api_client=job_api_client
        )

    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await self._job_api_client.get_health_check()

    async def fetch_job(self, session_id: str) -> GetJobResponse:
        """
        Fetches a job by session id

        Args:
            session_id (str): The session ID

        Returns:
            GetJobResponse: The job fetched
        """
        return await self._job_api_client.fetch_job(session_id=session_id)

    async def list_jobs(self, list_jobs_request: ListJobsRequest) -> ListJobsResponse:
        """
        Lists all jobs for the given user

        Args:
            list_jobs_request (ListJobsRequest): The request including details

        Returns:
            ListJobsResponse: The list of jobs
        """
        return await self._job_api_client.list_jobs(list_jobs_request=list_jobs_request)

    async def list_jobs_in_batch(self, list_request: ListByBatchRequest) -> ListByBatchResponse:
        """
        Gets all jobs within a batch.

        Args:
            list_request (ListByBatchRequest): The request including batch ID

        Returns:
            ListByBatchResponse: The response including list of jobs
        """
        return await self._job_api_client.list_jobs_in_batch(list_request=list_request)
