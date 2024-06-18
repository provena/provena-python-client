'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: Job API L2 Client.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from provenaclient.models import *
from ProvenaInterfaces.AsyncJobAPI import *


class JobAPIAdminEndpoints(str, Enum):
    """An ENUM containing the job api endpoints."""
    POST_JOBS_ADMIN_LAUNCH = "/jobs/admin/launch"
    GET_JOBS_ADMIN_FETCH = "/jobs/admin/fetch"
    POST_JOBS_ADMIN_LIST = "/jobs/admin/list"
    POST_JOBS_ADMIN_LIST_BATCH = "/jobs/admin/list_batch"

    # not implemented
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"


class JobAPIEndpoints(str, Enum):
    """An ENUM containing the job api endpoints."""
    GET_JOBS_USER_FETCH = "/jobs/user/fetch"
    POST_JOBS_USER_LIST = "/jobs/user/list"
    POST_JOBS_USER_LIST_BATCH = "/jobs/user/list_batch"

    # Done
    GET_HEALTH_CHECK = "/"

    # not implemented
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"

# L2 interface.


class JobAPIAdminSubClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the JobAPIAdminClient sub client with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: JobAPIAdminEndpoints) -> str:
        return self._config.jobs_service_api_endpoint + endpoint.value

    async def launch_job(self, request: AdminLaunchJobRequest) -> AdminLaunchJobResponse:
        """
        Launches a new job.

        Args:
            request (AdminLaunchJobRequest): Specified job parameters

        Returns:
            AdminLaunchJobResponse: The response
        """
        return await parsed_post_request(
            client=self,
            json_body=py_to_dict(request),
            params={},
            url=self._build_endpoint(
                JobAPIAdminEndpoints.POST_JOBS_ADMIN_LAUNCH),
            error_message=f"Failed to launch job of subtype {request.job_sub_type}.",
            model=AdminLaunchJobResponse
        )

    async def get_job(self, session_id: str) -> AdminGetJobResponse:
        """
        Fetches a job (any job since admin)

        Args:
            session_id (str): The session ID of job to fetch

        Returns:
            AdminGetJobResponse: The response
        """
        return await parsed_get_request(
            client=self,
            params={'session_id': session_id},
            url=self._build_endpoint(
                JobAPIAdminEndpoints.GET_JOBS_ADMIN_FETCH),
            error_message=f"Failed to fetch job (admin) for session id {session_id}",
            model=AdminGetJobResponse
        )

    async def list_jobs(self, list_jobs_request: AdminListJobsRequest) -> AdminListJobsResponse:
        """
        Lists all jobs.

        Args:
            list_jobs_request (AdminListJobsRequest): The request including pagination information.

        Returns:
            AdminListJobsResponse: The list of jobs response.
        """
        return await parsed_post_request(
            client=self,
            json_body=py_to_dict(list_jobs_request),
            params={},
            url=self._build_endpoint(
                JobAPIAdminEndpoints.POST_JOBS_ADMIN_LIST),
            error_message=f"Failed to list jobs for user (admin).",
            model=AdminListJobsResponse
        )

    async def list_jobs_in_batch(self, list_request: AdminListByBatchRequest) -> AdminListByBatchResponse:
        """
        List jobs by batch ID, returning a list of jobs in the batch.

        Args:
            list_request (AdminListByBatchRequest): The request including batch ID

        Returns:
            AdminListByBatchResponse: The list of jobs in the batch
        """
        return await parsed_post_request(
            client=self,
            json_body=py_to_dict(list_request),
            params={},
            url=self._build_endpoint(
                JobAPIAdminEndpoints.POST_JOBS_ADMIN_LIST_BATCH),
            error_message=f"Failed to list jobs for specified batch (admin).",
            model=AdminListByBatchResponse
        )


class JobAPIClient(ClientService):
    admin: JobAPIAdminSubClient

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

        self.admin = JobAPIAdminSubClient(auth=auth, config=config)

    def _build_endpoint(self, endpoint: JobAPIEndpoints) -> str:
        return self._config.jobs_service_api_endpoint + endpoint.value

    async def get_health_check(self) -> HealthCheckResponse:
        """
        Health check the API

        Returns:
            HealthCheckResponse: Response
        """
        return await parsed_get_request(
            client=self,
            url=self._build_endpoint(JobAPIEndpoints.GET_HEALTH_CHECK),
            error_message="Health check failed!",
            params={},
            model=HealthCheckResponse
        )

    async def fetch_job(self, session_id: str) -> GetJobResponse:
        """
        Fetches a job by session id

        Args:
            session_id (str): The session ID

        Returns:
            GetJobResponse: The job fetched
        """
        return await parsed_get_request(
            client=self,
            params={'session_id': session_id},
            url=self._build_endpoint(JobAPIEndpoints.GET_JOBS_USER_FETCH),
            error_message=f"Failed to fetch job for session id {session_id}",
            model=GetJobResponse
        )

    async def list_jobs(self, list_jobs_request: ListJobsRequest) -> ListJobsResponse:
        """
        Lists all jobs for the given user

        Args:
            list_jobs_request (ListJobsRequest): The request including details

        Returns:
            ListJobsResponse: The list of jobs
        """
        return await parsed_post_request(
            client=self,
            json_body=py_to_dict(list_jobs_request),
            params={},
            url=self._build_endpoint(JobAPIEndpoints.POST_JOBS_USER_LIST),
            error_message=f"Failed to list jobs for user.",
            model=ListJobsResponse
        )

    async def list_jobs_in_batch(self, list_request: ListByBatchRequest) -> ListByBatchResponse:
        """
        Gets all jobs within a batch.

        Args:
            list_request (ListByBatchRequest): The request including batch ID

        Returns:
            ListByBatchResponse: The response including list of jobs
        """
        return await parsed_post_request(
            client=self,
            json_body=py_to_dict(list_request),
            params={},
            url=self._build_endpoint(
                JobAPIEndpoints.POST_JOBS_USER_LIST_BATCH),
            error_message=f"Failed to list jobs for user by batch.",
            model=ListByBatchResponse
        )
