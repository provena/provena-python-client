from typing import Any, Optional
import httpx
from provenaclient.auth.auth_helpers import HttpxBearerAuth

# Have to add this or else HTTP request timesout.
timeout = httpx.Timeout(timeout = 10.0, connect = 60.0) 

class HttpClient: 

    @staticmethod
    async def make_get_request(url: str, params:Optional[dict[str, Any]] = None, auth: Optional[HttpxBearerAuth] = None, headers:Optional[dict[str,Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout) as client: 
            response = await client.get(url,params = params, headers= headers, auth=auth)
            return response

    @staticmethod    
    async def make_post_request(url: str, data: Optional[dict[str,Any]] = None, auth: Optional[HttpxBearerAuth] = None, headers: Optional[dict[str, Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=data, headers=headers, auth=auth) #type:ignore
            return response