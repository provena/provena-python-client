'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: Set of helpers for running polling tasks against the job API until completion etc.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from typing import Dict, Any, Callable, Optional, cast, Tuple, Coroutine
from ProvenaInterfaces.AsyncJobModels import JobStatusTable
from ProvenaInterfaces.AsyncJobAPI import *
from datetime import datetime
from time import sleep
from provenaclient.clients import JobAPIClient
from provenaclient.models import AsyncAwaitSettings
from provenaclient.utils.exceptions import BaseException

JOB_FINISHED_STATES = [JobStatus.FAILED, JobStatus.SUCCEEDED]

Payload = Dict[str, Any]


def timestamp() -> int:
    return int(datetime.now().timestamp())


# finished? optional data
PollCallbackData = Optional[Any]
PollCallbackResponse = Tuple[bool, PollCallbackData]
PollCallbackFunction = Callable[[],
                                Coroutine[Any, Any, PollCallbackResponse]]


class PollTimeoutException(Exception):
    "Raised when poll operation exceeds timeout"
    pass


class PollFunctionErrorException(Exception):
    "Raised when poll operation callback errors"
    pass


async def poll_callback(poll_interval_seconds: int, timeout_seconds: int, callback: PollCallbackFunction) -> PollCallbackData:
    """
    The poll callback function which repeatedly polls given func according to spec

    Args:
        poll_interval_seconds (int): The polling interval
        timeout_seconds (int): The timeout to adhere to
        callback (PollCallbackFunction): The call back function itself

    Raises:
        PollFunctionErrorException: Unexpected error
        PollTimeoutException: Timeout

    Returns:
        PollCallbackData: The resulting data (job status table probably)
    """
    start_time = timestamp()
    completed = False
    data = None

    def timeout_condition_check() -> bool:
        curr = timestamp()
        return curr - start_time <= timeout_seconds

    def print_status() -> None:
        print(
            f"Polling Job API. Wait time: {round(timestamp() - start_time,2)}sec out of {timeout_seconds}sec.")

    while (not completed) and timeout_condition_check():
        print_status()

        try:
            fin, res_data = await callback()
        except Exception as e:
            raise PollFunctionErrorException(
                f"Polling callback function raised an error. Aborting. Error: {e}.")

        if fin:
            data = res_data
            completed = True
        else:
            print("Callback registered incomplete. Waiting for polling interval.")
            sleep(poll_interval_seconds)

    if completed:
        return data
    else:
        raise PollTimeoutException("Timed out during polling operation.")


async def wait_for_in_progress(session_id: str, client: JobAPIClient, settings: AsyncAwaitSettings) -> JobStatusTable:
    """
    Waits for the entry to be in in progress status

    Args:
        session_id (str): The session ID
        client (JobAPIClient): The L2 job client
        settings (AsyncAwaitSettings): The settings

    Returns:
        JobStatusTable: The resulting entry
    """
    timeout = settings.job_async_pending_polling_timeout
    interval = settings.job_polling_interval

    async def callback() -> PollCallbackResponse:
        print(
            f"Running wait for in progress callback. Session ID: {session_id}.")
        entry = (await client.fetch_job(session_id=session_id)).job

        # stop if we exit pending - could jump straight to error/success otherwise
        if entry.status != JobStatus.PENDING:
            print(
                f"200OK response for user fetch of {session_id} in non pending state {entry.status}.")
            return True, entry
        else:
            print(
                f"200OK response for user fetch of {session_id} in state {entry.status}.")
            return False, None

    # poll
    print(f"Starting wait_for_in_progress polling stage.")
    data = await poll_callback(
        poll_interval_seconds=interval,
        timeout_seconds=timeout,
        callback=callback
    )
    print(f"Finished wait_for_in_progress polling stage.")

    assert data is not None
    return cast(JobStatusTable, data)


async def wait_for_entry_in_queue(session_id: str, client: JobAPIClient, settings: AsyncAwaitSettings) -> JobStatusTable:
    """
    Waits for the entry to appear in the queue

    Args:
        session_id (str): The session ID
        client (JobAPIClient): The L2 job client
        settings (AsyncAwaitSettings): The settings

    Raises:
        Exception: If non 400 error

    Returns:
        JobStatusTable: The resulting entry
    """
    timeout = settings.job_async_queue_delay_polling_timeout
    interval = settings.job_polling_interval

    async def callback() -> PollCallbackResponse:
        print(
            f"Running wait_for_entry_in_queue callback. Session ID: {session_id}.")
        try:
            job = await client.fetch_job(session_id=session_id)
        except BaseException as be:
            if be.error_code != 400:
                raise Exception(
                    f"Unexpected error state when waiting for job. Code: {be.error_code}. Error: {be.message}.") from be
            else:
                return False, None

        print(f"200OK response for user fetch of {session_id}.")
        # Parse and return the 200OK data
        entry: JobStatusTable = job.job
        return True, entry

    # poll
    print(f"Starting wait_for_entry_in_queue polling stage.")
    data = await poll_callback(
        poll_interval_seconds=interval,
        timeout_seconds=timeout,
        callback=callback
    )
    print(f"Finished wait_for_entry_in_queue polling stage.")

    return cast(JobStatusTable, data)


async def wait_for_completion(session_id: str, client: JobAPIClient, settings: AsyncAwaitSettings) -> JobStatusTable:
    """
    Waits for completion.

    Args:
        session_id (str): The session ID
        client (JobAPIClient): The L2 job client
        settings (AsyncAwaitSettings): The settings

    Returns:
        JobStatusTable: The resulting entry
    """
    timeout = settings.job_async_in_progress_polling_timeout
    interval = settings.job_polling_interval

    async def callback() -> PollCallbackResponse:
        print(
            f"Running wait for completion callback. Session ID: {session_id}.")

        data = await client.fetch_job(session_id=session_id)
        entry = data.job

        # stop if we exit pending - could jump straight to error/success otherwise
        if entry.status in JOB_FINISHED_STATES:
            print(
                f"200OK response for user fetch of {session_id} in completed state.")
            return True, entry
        else:
            print(
                f"200OK response for user fetch of {session_id} in state {entry}.")
            return False, None

    # poll
    print(f"Starting wait_for_completion polling stage.")
    data = await poll_callback(
        poll_interval_seconds=interval,
        timeout_seconds=timeout,
        callback=callback
    )
    print(f"Finished wait_for_completion polling stage.")

    assert data is not None
    return cast(JobStatusTable, data)


async def wait_for_full_lifecycle(session_id: str, client: JobAPIClient, settings: AsyncAwaitSettings) -> JobStatusTable:
    """

    Waits for the entire lifecycle of a job, adhering to settings. Uses L2 client.

    Args:
        session_id (str): The session ID to await
        client (JobAPIClient): The client to utilise
        settings (AsyncAwaitSettings): The settings including timeouts

    Returns:
        JobStatusTable: The resulting entry
    """
    # wait for item to be present in job table - could take a few seconds
    data = await wait_for_entry_in_queue(session_id=session_id, client=client, settings=settings)

    # backout early
    if data.status in JOB_FINISHED_STATES:
        return data

    # block into two steps to time separately
    data = await wait_for_in_progress(session_id=session_id, client=client, settings=settings)

    # backout early
    if data.status in JOB_FINISHED_STATES:
        return data

    return await wait_for_completion(session_id=session_id, client=client, settings=settings)


async def wait_for_full_successful_lifecycle(session_id: str,  client: JobAPIClient, settings: AsyncAwaitSettings) -> JobStatusTable:
    """
    Waits for the full lifecycle of an async job and asserts that it is successful at the end.

    Args:
        session_id (str): The session ID to await
        client (JobAPIClient): The client 
        settings (AsyncAwaitSettings): The settings

    Returns:
        JobStatusTable: The resulting successful job
    """
    res = await wait_for_full_lifecycle(session_id=session_id, client=client, settings=settings)

    assert res.status == JobStatus.SUCCEEDED, \
        f"Job failed, error {res.info or 'None provided'}. Session ID {session_id}."

    assert res.result is not None, \
        f"Job succeeded, but did not include a result payload!"

    return res
