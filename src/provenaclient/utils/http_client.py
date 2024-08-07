"""
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 5:00:47 pm +1000
Modified By: Peter Baker
-----
Description: A HTTP client which wraps HTTPx async so that we can swap out a different http library later if needed.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
"""

from typing import Any, List, Optional, Union
import httpx
from provenaclient.auth.helpers import HttpxBearerAuth
from provenaclient.utils.helpers import JsonData

# 30s total timeout (mirroring API Gateway timeout anyway)
timeout = httpx.Timeout(timeout=30.0)

# L1 interface.


class HttpClient:
    """This class only contains static methods as it acts as an HTTP client and provides a layer over these static methods
    and makes them easily identifiable within the codebase.
    """

    @staticmethod
    async def make_get_request(
        url: str,
        params: Optional[dict[str, Any]] = None,
        auth: Optional[HttpxBearerAuth] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Makes an asynchronous HTTP GET request to the specified URL using the provided parameters, authentication, and headers.

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
            response = await client.get(url, params=params, headers=headers, auth=auth)
            return response

    @staticmethod
    async def make_delete_request(
        url: str,
        auth: HttpxBearerAuth,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Makes an asynchronous HTTP DELETE request to the specified URL using the provided parameters, authentication, and headers.

        Parameters
        ----------
        url : str
            The URL to which the DELETE request will be sent.
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
            response = await client.delete(
                url, params=params, headers=headers, auth=auth
            )
            return response

    @staticmethod
    async def make_post_request(
        url: str,
        auth: HttpxBearerAuth,
        params: Optional[dict[str, Any]] = None,
        data: Union[Optional[dict[str, Any]], Optional[List[dict[str, Any]]]] = None,
        files: Optional[dict[str, tuple[str, bytes, str]]] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Makes an asynchronous HTTP POST request to the specified URL with the provided data, authentication, and headers.

        Parameters
        ----------
        url : str
            The URL to which the GET request will be sent.
        params : Optional[dict[str, Any]], optional
            A dictionary of the query parameters to be included in the GET request, by default None.
        auth : HttpxBearerAuth
            Authentication object (e.g., bearer token), which is required for the POST request.
        data : Optional[dict[str,Any]], optional
            A dictionary of the data to be sent in the body of the POST request, by default None.
        files: Optional[dict[str, tuple[str, bytes, str]]], optional
            A files request object containing the file content and the media type.
        headers : Optional[dict[str, Any]], optional
            A dictionary representing additional HTTP headers to send with the POST request, by default None.

        Returns
        -------
        httpx.Response
            The response from the server as an httpx.Response object.
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url, params=params, json=data, headers=headers, files=files, auth=auth
            )
            return response

    @staticmethod
    async def make_put_request(
        url: str,
        auth: HttpxBearerAuth,
        params: Optional[dict[str, Any]] = None,
        data: Optional[JsonData] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Makes an asynchronous HTTP put request to the specified URL with the provided data, authentication, and headers.

        Parameters
        ----------
        url : str
            The URL to which the GET request will be sent.
        params : Optional[dict[str, Any]], optional
            A dictionary of the query parameters to be included in the GET request, by default None.
        auth : HttpxBearerAuth
            Authentication object (e.g., bearer token), which is required for the put request.
        data : Optional[dict[str,Any]], optional
            A dictionary of the data to be sent in the body of the put request, by default None.
        headers : Optional[dict[str, Any]], optional
            A dictionary representing additional HTTP headers to send with the put request, by default None.

        Returns
        -------
        httpx.Response
            The response from the server as an httpx.Response object.
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.put(
                url, params=params, json=data, headers=headers, auth=auth
            )
            return response
