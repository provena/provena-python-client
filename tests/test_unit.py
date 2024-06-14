import json
from provenaclient.utils.http_client import HttpClient, HttpxBearerAuth
from provenaclient.utils.exceptions import CustomTimeoutException
import pytest
import httpx
from pytest_httpx import HTTPXMock


"""L1 Layer Testing With No Real API/HTTP Server"""

@pytest.mark.asyncio
async def test_http_client_get_request(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient GET method, checking both the request made and the response received."""
    url = "https://api.example.com/data"
    httpx_mock.add_response(method="GET", url=url, json={"success": True}, status_code=200)

    response = await HttpClient.make_get_request(url)
    assert response.status_code == 200 and response.json() == {"success": True}
    
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "GET" and str(request.url) == url

@pytest.mark.asyncio
async def test_http_client_get_request_errors(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient GET method for handling server errors."""
    url = "https://api.example.com/data"

    httpx_mock.add_response(method="GET", url=url, json={"error": "Internal Server Error"}, status_code=500)

    response = await HttpClient.make_get_request(url)
    assert response.status_code == 500
    assert response.json() == {"error": "Internal Server Error"}


@pytest.mark.asyncio
async def test_http_client_post_request(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient POST method, checking both the request made and the response received for different scenarios."""
    url = "https://api.example.com/data"
    data = {"key": "value"}
    fake_auth = HttpxBearerAuth(token="fake-token")
    file_payload = {"csv_file": ("upload.csv", b"hnsdhn3y3nydsndyndheef", "text/csv")}

    # Valid authentication
    httpx_mock.add_response(method="POST", url=url, json={"success": True}, status_code=200)
    response = await HttpClient.make_post_request(url, data=data, auth=fake_auth)
    assert response.status_code == 200 and response.json() == {"success": True}
    
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "POST"
    assert request.headers.get("Authorization") == "Bearer " + fake_auth.token
    assert json.loads(request.read()) == data

    # File upload
    httpx_mock.add_response(method="POST", url=url, status_code=200)
    response = await HttpClient.make_post_request(url, files=file_payload, auth=fake_auth)
    assert response.status_code == 200
    
    file_request = httpx_mock.get_requests()[-1]
    assert file_request is not None, "No request was made."

    assert file_request.method == "POST"
    assert file_request.headers.get("Content-Type").startswith("multipart/form-data")
    assert b"csv_file" in file_request.read() and b"text/csv" in file_request.read()


@pytest.mark.asyncio
async def test_http_client_post_request_errors(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient POST method for handling authentication and validation errors."""
    url = "https://api.example.com/data"
    data = {"key": "value"}
    fake_auth = HttpxBearerAuth(token="fake-token")

    # Auth error (401)
    httpx_mock.add_response(method="POST", url=url, json={"error": "Unauthorized"}, status_code=401)
    response = await HttpClient.make_post_request(url, data=data, auth=fake_auth)
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}

    # HTTP Validation error (422)
    httpx_mock.add_response(method="POST", url=url, json={"error": "Unprocessable Entity"}, status_code=422)
    response = await HttpClient.make_post_request(url, data=data, auth=fake_auth)
    assert response.status_code == 422
    assert response.json() == {"error": "Unprocessable Entity"}


@pytest.mark.asyncio
async def test_http_client_delete_request(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient DELETE method, checking both the request made and the response received."""
    url = "https://api.example.com/data"
    params = {"id": 2}
    final_url = httpx.URL(url, params = params)
    fake_auth = HttpxBearerAuth(token="fake-token")

    httpx_mock.add_response(method="DELETE", url=final_url, status_code=200)
    response = await HttpClient.make_delete_request(url, params=params, auth=fake_auth)
    
    assert response.status_code == 200
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "DELETE"
    assert str(request.url) == final_url

@pytest.mark.asyncio
async def test_http_client_put_request(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient PUT method, checking both the request made and the response received."""
    url = "https://api.example.com/data"
    data = {"item": "someItem"}
    fake_auth = HttpxBearerAuth(token="fake-token")

    httpx_mock.add_response(method="PUT", url=url, json={"updated": True}, status_code=200)
    response = await HttpClient.make_put_request(url, data=data, auth=fake_auth)

    assert response.status_code == 200 and response.json() == {"updated": True}
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "PUT"
    assert str(request.url) == url
    assert json.loads(request.read()) == data

@pytest.mark.asyncio
async def test_http_client_put_request_errors(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient PUT method for handling bad request error due to missing data."""
    url = "https://api.example.com/data"
    
    # Imagine there is a missing parameter here. 
    incomplete_data = {"item": "someItem"}

    fake_auth = HttpxBearerAuth(token="fake-token")

    # Bad request error. 
    httpx_mock.add_response(method="PUT", url=url, json={"error": "Bad Request", "message": "Missing 'userId'"}, status_code=400)
    response = await HttpClient.make_put_request(url, data=incomplete_data, auth=fake_auth)

    assert response.status_code == 400
    assert response.json() == {"error": "Bad Request", "message": "Missing 'userId'"}, "The response should contain missing parameter userId, however it seems to be there."

    request = httpx_mock.get_request()
    assert request is not None, "No request was made."
    assert request.method == "PUT"
    assert str(request.url) == url
    assert json.loads(request.read()) == incomplete_data, "The request payload does not match the incomplete data sent."


"""L1 Layer Testing With Real API/HTTP Server (HttpBin)"""


    
    
