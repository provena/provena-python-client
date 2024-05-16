from typing import Dict, Any, Optional
import httpx

class HttpClient: 

    @staticmethod
    async def make_get_request(url: str, params:Optional[dict[str, Any]] = None, headers:Optional[dict[str,Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient() as client: 
            response = await client.get(url,params = params, headers= headers)
            return response

    @staticmethod    
    async def make_post_request(url: str, data: Optional[dict[str, Any]] = None, headers: Optional[dict[str, Any]] = None) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json = data, headers = headers)
            return response