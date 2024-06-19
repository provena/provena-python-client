import json
from provenaclient.utils.http_client import HttpClient, HttpxBearerAuth
from provenaclient.utils.exceptions import CustomTimeoutException
import pytest
import httpx
from pytest_httpx import HTTPXMock



@pytest.fixture
# Valid token fixture.
def valid_token() -> HttpxBearerAuth:
    return HttpxBearerAuth(token="valid-token")


@pytest.fixture
# Invalid token fixture.
def invalid_token() -> HttpxBearerAuth:
    return HttpxBearerAuth(token="invalid-token")

"""L1 Layer Testing With No Real API/HTTP Server

   Created mock tests across all HTTP METHOD types and 
   various status code errors.

"""

@pytest.mark.asyncio
async def test_http_client_get_request_mock(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient GET method, checking both the request made and the response received."""
    url = "https://api.example.com/data"
    httpx_mock.add_response(method="GET", url=url, json={"success": True}, status_code=200)

    response = await HttpClient.make_get_request(url)
    assert response.status_code == 200 and response.json() == {"success": True}
    
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "GET" and str(request.url) == url

@pytest.mark.asyncio
async def test_http_client_get_request_errors_mock(httpx_mock: HTTPXMock) -> None:
    """Tests HttpClient GET method for handling server errors."""
    url = "https://api.example.com/data"

    httpx_mock.add_response(method="GET", url=url, json={"error": "Internal Server Error"}, status_code=500)

    response = await HttpClient.make_get_request(url)
    assert response.status_code == 500
    assert response.json() == {"error": "Internal Server Error"}


@pytest.mark.asyncio
async def test_http_client_post_request_mock(httpx_mock: HTTPXMock, valid_token: HttpxBearerAuth) -> None:
    """Tests HttpClient POST method, checking both the request made and the response received for different scenarios."""
    url = "https://api.example.com/data"
    data = {"key": "value"}
    file_payload = {"csv_file": ("upload.csv", b"hnsdhn3y3nydsndyndheef", "text/csv")}

    # Valid authentication
    httpx_mock.add_response(method="POST", url=url, json={"success": True}, status_code=200)
    response = await HttpClient.make_post_request(url, data=data, auth=valid_token)
    assert response.status_code == 200 and response.json() == {"success": True}
    
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "POST"
    assert request.headers.get("Authorization") == "Bearer " + valid_token.token
    assert json.loads(request.read()) == data

    # File upload
    httpx_mock.add_response(method="POST", url=url, status_code=200)
    response = await HttpClient.make_post_request(url, files=file_payload, auth=valid_token)
    assert response.status_code == 200
    
    # Get the last/newest request.
    file_request = httpx_mock.get_requests()[-1]
    assert file_request is not None, "No request was made."

    assert file_request.method == "POST"
    assert file_request.headers.get("Content-Type").startswith("multipart/form-data")
    assert b"csv_file" in file_request.read() and b"text/csv" in file_request.read()


@pytest.mark.asyncio
async def test_http_client_post_request_mock_errors(httpx_mock: HTTPXMock, invalid_token: HttpxBearerAuth, valid_token: HttpxBearerAuth) -> None:
    """Tests HttpClient POST method for handling authentication and validation errors."""
    url = "https://api.example.com/data"
    data = {"key": "value"}

    # Auth error (401) with invalid token.
    httpx_mock.add_response(method="POST", url=url, json={"error": "Unauthorized"}, status_code=401)
    response = await HttpClient.make_post_request(url, data=data, auth=invalid_token)
    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}

    # HTTP Validation error (422) with valid token.
    httpx_mock.add_response(method="POST", url=url, json={"error": "Unprocessable Entity"}, status_code=422)
    response = await HttpClient.make_post_request(url, data=data, auth=valid_token)
    assert response.status_code == 422
    assert response.json() == {"error": "Unprocessable Entity"}


@pytest.mark.asyncio
async def test_http_client_delete_request_mock(httpx_mock: HTTPXMock, valid_token: HttpxBearerAuth) -> None:
    """Tests HttpClient DELETE method, checking both the request made and the response received."""
    url = "https://api.example.com/data"
    params = {"id": 2}
    final_url = httpx.URL(url, params = params) # Inserts params into base url. 

    httpx_mock.add_response(method="DELETE", url=final_url, status_code=200)
    response = await HttpClient.make_delete_request(url, params=params, auth=valid_token)
    
    assert response.status_code == 200
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "DELETE"
    assert str(request.url) == final_url

@pytest.mark.asyncio
async def test_http_client_put_request_mock(httpx_mock: HTTPXMock, valid_token: HttpxBearerAuth) -> None:
    """Tests HttpClient PUT method, checking both the request made and the response received."""
    url = "https://api.example.com/data"
    data = {"item": "someItem"}

    httpx_mock.add_response(method="PUT", url=url, json={"updated": True}, status_code=200)
    response = await HttpClient.make_put_request(url, data=data, auth=valid_token)

    assert response.status_code == 200 and response.json() == {"updated": True}
    request = httpx_mock.get_request()
    assert request is not None, "No request was made."

    assert request.method == "PUT"
    assert str(request.url) == url
    assert json.loads(request.read()) == data

@pytest.mark.asyncio
async def test_http_client_put_request_mock_errors(httpx_mock: HTTPXMock, valid_token: HttpxBearerAuth) -> None:
    """Tests HttpClient PUT method for handling bad request error due to missing data."""
    url = "https://api.example.com/data"
    
    # Imagine there is a missing parameter here. 
    incomplete_data = {"item": "someItem"}

    # Bad request error. 
    httpx_mock.add_response(method="PUT", url=url, json={"error": "Bad Request", "message": "Missing 'userId'"}, status_code=400)
    response = await HttpClient.make_put_request(url, data=incomplete_data, auth=valid_token)

    assert response.status_code == 400
    assert response.json() == {"error": "Bad Request", "message": "Missing 'userId'"}, "The response should contain missing parameter userId, however it seems to be there."

    request = httpx_mock.get_request()
    assert request is not None, "No request was made."
    assert request.method == "PUT"
    assert str(request.url) == url
    assert json.loads(request.read()) == incomplete_data, "The request payload does not match the incomplete data sent."


"""L1 Layer Testing With Real API/HTTP Server (JSONPlaceHolder)

   JSONPlaceHolder has very limited functionality, hence at most 
   404 can be tested easily for negative testing.

"""

@pytest.mark.asyncio
async def test_http_client_get_request() -> None:
    """Tests 200OK status for GET request"""
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = await HttpClient.make_get_request(url)

    assert response.status_code == 200
    json_response = response.json()

    assert "userId" in json_response
    assert "id" in json_response
    assert "title" in json_response
    assert "body" in json_response

@pytest.mark.asyncio
async def test_http_client_post_request(valid_token: HttpxBearerAuth) -> None:
    """Tests 201 Created status for POST request."""
    url = "https://jsonplaceholder.typicode.com/posts"
    data = {"title": "foo", "body": "bar", "userId": 1}
    response = await HttpClient.make_post_request(url, data=data, auth=valid_token)

    assert response.status_code == 201
    assert response.json() == {"id": 101, "title": "foo", "body": "bar", "userId": 1}


@pytest.mark.asyncio
async def test_http_client_put_request(valid_token: HttpxBearerAuth) -> None:
    """Tests 200OK status for PUT request."""
    url = "https://jsonplaceholder.typicode.com/posts/1"
    data = {"id": 1, "title": "foo", "body": "bar", "userId": 1}
    response = await HttpClient.make_put_request(url, data=data, auth=valid_token)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "foo", "body": "bar", "userId": 1}

@pytest.mark.asyncio
async def test_http_client_delete_request(valid_token: HttpxBearerAuth) -> None:
    """Tests 200OK status for DELETE request."""
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = await HttpClient.make_delete_request(url, auth=valid_token)

    assert response.status_code == 200
    assert response.json() == {}  # JSONPlaceholder returns an empty object for successful DELETE

@pytest.mark.asyncio
async def test_http_client_post_request_errors(valid_token: HttpxBearerAuth) -> None:
    """Tests 404 error for HTTP request."""
    url = "https://jsonplaceholder.typicode.com/posts/25" # Invalid URL.
    data = {"title": None, "body": "bar", "userId": 1}
    response = await HttpClient.make_post_request(url, data=data, auth=valid_token)

    assert response.status_code == 404
    assert response.json() == {}

    
    
