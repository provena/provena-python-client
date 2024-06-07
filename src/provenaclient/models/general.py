from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    message: str

class AsyncAwaitSettings(BaseModel):
    # polling interval in seconds (defaults to 2 seconds)
    job_polling_interval : int = 2
        
    # how long do we wait for the entry to be present in table? (seconds)
    job_async_queue_delay_polling_timeout = 20  # 20 seconds

    # how long do we wait for it to leave pending? (seconds)
    job_async_pending_polling_timeout = 120  # 2 minutes

    # how long do we wait for it to become in progress? (seconds)
    job_async_in_progress_polling_timeout = 180  # 3 minutes
   
DEFAULT_AWAIT_SETTINGS = AsyncAwaitSettings()