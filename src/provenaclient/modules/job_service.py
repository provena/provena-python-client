'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: Job API L3 Module. Includes Job Admin sub module.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import JobAPIClient
from provenaclient.utils.exceptions import *
from provenaclient.modules.module_helpers import *
from provenaclient.models import HealthCheckResponse, AsyncAwaitSettings, DEFAULT_AWAIT_SETTINGS
from provenaclient.utils.async_job_helpers import wait_for_full_lifecycle, wait_for_full_successful_lifecycle
from ProvenaInterfaces.AsyncJobAPI import *
from typing import List, AsyncGenerator

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
    
    async def list_all_jobs(self, list_jobs_request: AdminListJobsRequest, limit: Optional[int] = None) -> List[JobStatusTable]:
        """
        Lists all jobs for the given user.

        Will automatically paginate until list is exhausted.

        Args:
            list_jobs_request (AdminListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        all_jobs: List[JobStatusTable] = []
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.admin.list_jobs(list_jobs_request=list_jobs_request)
            count += len(new_list.jobs)
            all_jobs.extend(new_list.jobs)

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_jobs_request.pagination_key = new_list.pagination_key

        return all_jobs

    async def for_all_jobs(self, list_jobs_request: AdminListJobsRequest, limit: Optional[int] = None) -> AsyncGenerator[JobStatusTable, None]:
        """
        Lists all jobs for the given user.

        Returns lazy generator for use in for loops.

        Will automatically paginate until list is exhausted.

        Args:
            list_jobs_request (AdminListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.admin.list_jobs(list_jobs_request=list_jobs_request)
            count += len(new_list.jobs)

            for job in new_list.jobs:
                yield job

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_jobs_request.pagination_key = new_list.pagination_key
    

    async def list_job_batch(self, list_request: AdminListByBatchRequest) -> AdminListByBatchResponse:
        """
        List jobs by batch ID, returning a list of jobs in the batch.

        Args:
            list_request (AdminListByBatchRequest): The request including batch ID

        Returns:
            AdminListByBatchResponse: The list of jobs in the batch
        """
        return await self._job_api_client.admin.list_jobs_in_batch(list_request=list_request)

    async def list_all_jobs_in_batch(self, list_request: AdminListByBatchRequest, limit: Optional[int] = None) -> List[JobStatusTable]:
        """
        Lists all jobs for the given user. Will automatically paginate all
        entries to exhaust list 

        NOTE this could return more than limit - but figure it may as well
        return data fetched for efficiency reasons

        Args:
            list_jobs_request (AdminListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        all_jobs: List[JobStatusTable] = []
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.admin.list_jobs_in_batch(list_request=list_request)
            count += len(new_list.jobs)
            all_jobs.extend(new_list.jobs)

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_request.pagination_key = new_list.pagination_key

        return all_jobs

    async def for_all_jobs_in_batch(self, list_request: AdminListByBatchRequest, limit: Optional[int] = None) -> AsyncGenerator[JobStatusTable, None]:
        """
        Lists all jobs for the given user. Will automatically paginate all
        entries to exhaust list

        NOTE this could return more than limit - but figure it may as well
        return data fetched for efficiency reasons

        Args:
            list_jobs_request (AdminListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.admin.list_jobs_in_batch(list_request=list_request)
            count += len(new_list.jobs)

            for job in new_list.jobs:
                yield job

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_request.pagination_key = new_list.pagination_key

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

        Can return pagination if page size exceeded

        Args:
            list_jobs_request (ListJobsRequest): The request including details

        Returns:
            ListJobsResponse: The list of jobs
        """
        return await self._job_api_client.list_jobs(list_jobs_request=list_jobs_request)

    async def list_all_jobs(self, list_jobs_request: ListJobsRequest, limit: Optional[int] = None) -> List[JobStatusTable]:
        """
        Lists all jobs for the given user.

        Will automatically paginate until list is exhausted.

        Args:
            list_jobs_request (ListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        all_jobs: List[JobStatusTable] = []
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.list_jobs(list_jobs_request=list_jobs_request)
            count += len(new_list.jobs)
            all_jobs.extend(new_list.jobs)

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_jobs_request.pagination_key = new_list.pagination_key

        return all_jobs

    async def for_all_jobs(self, list_jobs_request: ListJobsRequest, limit: Optional[int] = None) -> AsyncGenerator[JobStatusTable, None]:
        """
        Lists all jobs for the given user.

        Returns lazy generator for use in for loops.

        Will automatically paginate until list is exhausted.

        Args:
            list_jobs_request (ListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.list_jobs(list_jobs_request=list_jobs_request)
            count += len(new_list.jobs)

            for job in new_list.jobs:
                yield job

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_jobs_request.pagination_key = new_list.pagination_key

    async def list_jobs_in_batch(self, list_request: ListByBatchRequest) -> ListByBatchResponse:
        """
        Gets all jobs within a batch.

        Can return pagination if page size exceeded

        Args:
            list_request (ListByBatchRequest): The request including batch ID

        Returns:
            ListByBatchResponse: The response including list of jobs
        """
        return await self._job_api_client.list_jobs_in_batch(list_request=list_request)

    async def list_all_jobs_in_batch(self, list_request: ListByBatchRequest, limit: Optional[int] = None) -> List[JobStatusTable]:
        """
        Lists all jobs for the given user. Will automatically paginate all
        entries to exhaust list 

        NOTE this could return more than limit - but figure it may as well
        return data fetched for efficiency reasons

        Args:
            list_jobs_request (ListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        all_jobs: List[JobStatusTable] = []
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.list_jobs_in_batch(list_request=list_request)
            count += len(new_list.jobs)
            all_jobs.extend(new_list.jobs)

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_request.pagination_key = new_list.pagination_key

        return all_jobs

    async def for_all_jobs_in_batch(self, list_request: ListByBatchRequest, limit: Optional[int] = None) -> AsyncGenerator[JobStatusTable, None]:
        """
        Lists all jobs for the given user. Will automatically paginate all
        entries to exhaust list

        NOTE this could return more than limit - but figure it may as well
        return data fetched for efficiency reasons

        Args:
            list_jobs_request (ListJobsRequest): The request including details
            limit (Optional[int]): Total record limit to enforce, if any

        Returns:
            ListJobsResponse: The list of jobs
        """
        count = 0

        # paginate until limit hit
        while True:
            new_list = await self._job_api_client.list_jobs_in_batch(list_request=list_request)
            count += len(new_list.jobs)

            for job in new_list.jobs:
                yield job

            if limit is not None and count >= limit:
                break

            if new_list.pagination_key is None:
                break

            list_request.pagination_key = new_list.pagination_key

    async def await_job_completion(self, session_id: str, settings: AsyncAwaitSettings = DEFAULT_AWAIT_SETTINGS) -> JobStatusTable:
        """

        Awaits completion of a given job then provides the job info.

        Completion is defined as a job status which is not pending or in progress.

        Args:
            session_id (str): The ID of the job to monitor and await completion.

        Returns:
            JobStatusTable: The entry at the latest point.
        """

        return await wait_for_full_lifecycle(
            session_id=session_id,
            client=self._job_api_client,
            settings=settings
        )

    async def await_successful_job_completion(self, session_id: str, settings: AsyncAwaitSettings = DEFAULT_AWAIT_SETTINGS) -> JobStatusTable:
        """

        Awaits successful completion of a given job then provides the job info.

        Completion is defined as a job status which is not pending or in progress.

        Args:
            session_id (str): The ID of the job to monitor and await completion.

        Returns:
            JobStatusTable: The entry at the latest point.
        """

        return await wait_for_full_successful_lifecycle(
            session_id=session_id,
            client=self._job_api_client,
            settings=settings
        )
