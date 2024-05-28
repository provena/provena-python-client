from typing import Any, Optional
import httpx
from provenaclient.auth.helpers import HttpxBearerAuth

#60s timeout for connecting, and a 10s timeout elsewhere.
timeout = httpx.Timeout(timeout = 10.0, connect = 60.0) 

#L1 interface.

class HttpClient: 

    """This class only contains static methods as it acts as an HTTP client and provides a layer over these static methods 
    and makes them easily identifiable within the codebase.
    """

    @staticmethod
    async def make_get_request(url: str, params:Optional[dict[str, Any]] = None, auth: Optional[HttpxBearerAuth] = None, headers:Optional[dict[str,Any]] = None) -> httpx.Response:
        """ Makes an asynchronous HTTP GET request to the specified URL using the provided parameters, authentication, and headers.

        Parameters
        ----------
        url : str
            The URL to which the GET request will be sent.
        params : Optional[dict[str, Any]], optional
            A dictionary of the query parameters to be included in the GET request, by default None.
        auth : Optional[HttpxBearerAuth], optional
            Authentication object (httpx bearer token only), to be included in the request headers, by default None.
        headers : Optional[dict[str,Any]], optional
            A dictionary having additional HTTP headers to send with the GET request, by default None.

        Returns
        -------
        httpx.Response
            The response from the server as an httpx.Response object.
        """
        async with httpx.AsyncClient(timeout=timeout) as client: 
            response = await client.get(url,params = params, headers= headers, auth=auth)
            return response

    @staticmethod    
    async def make_post_request(url: str, auth: HttpxBearerAuth, data: Optional[dict[str,Any]] = None, headers: Optional[dict[str, Any]] = None) -> httpx.Response:
        """ Makes an asynchronous HTTP POST request to the specified URL with the provided data, authentication, and headers.

        Parameters
        ----------
        url : str
            The URL to which the GET request will be sent.
        auth : HttpxBearerAuth
            Authentication object (e.g., bearer token), which is required for the POST request.
        data : Optional[dict[str,Any]], optional
            A dictionary of the data to be sent in the body of the POST request, by default None.
        headers : Optional[dict[str, Any]], optional
            A dictionary representing additional HTTP headers to send with the POST request, by default None.

        Returns
        -------
        httpx.Response
            The response from the server as an httpx.Response object.
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=data, headers=headers, auth=auth)
            return response