import json

from provenaclient.clients.client_helpers import parsed_delete_request, parsed_delete_request_with_status, parsed_get_request, parsed_post_request, parsed_put_request, parsed_put_request_with_status
from provenaclient.utils.helpers import build_params_exclude_none, py_to_dict
from provenaclient.utils.http_client import HttpClient, HttpxBearerAuth
from provenaclient.utils.exceptions import AuthException, BadRequestException, CustomTimeoutException, HTTPValidationException, ServerException, ValidationException
import pytest
import httpx
from pytest_httpx import HTTPXMock
from ProvenaInterfaces.SharedTypes import StatusResponse, Status


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



"""L2 Layer Testing

  Defining the components that are used: 

  1. Auth Service
  2. Client

"""

from unit_helpers import MockedClientService, MockedAuthService, MockRequestModel, MockResponseModel
from provenaclient.utils.config import Config

@pytest.fixture
def mock_auth_manager() -> MockedAuthService:
    return MockedAuthService()

@pytest.fixture
def client_service(mock_auth_manager: MockedAuthService) -> MockedClientService:

    mocked_config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    return MockedClientService(auth=mock_auth_manager, config=mocked_config)

"""Testing Exceptions on L2 Layer

   This will occur on all the higher level functions within client_helpers.py

   1. Focusing on direct requests that don't return status models and others that return status models.

      - Base Exceptions (Timeout, HTTP Validation, Unauthorised)

"""

"""Failure to connect, wrong or incorrect hostname simulations

  These three tests below are being caught very generally itself within 
  exceptions, and not within a specific exception itself by the client library.

"""

@pytest.mark.asyncio
async def test_request_connect_error(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Connection error has occurred."

    # GET Request. 
    httpx_mock.add_exception(httpx.ConnectError(message="Failed to connect."), method = "GET", url= url )
    
    with pytest.raises(Exception) as exc_info:
        await parsed_get_request(client=client_service, url=url, params=None, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info.value)

    # POST Request
    httpx_mock.add_exception(httpx.ConnectError(message=error_message), method = "POST", url= url )

    with pytest.raises(Exception) as exc_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info.value)

    # DELETE Request
    httpx_mock.add_exception(httpx.ConnectError(message=error_message), method = "DELETE", url= url )

    with pytest.raises(Exception) as exc_info:
        await parsed_delete_request(client=client_service, url=url, params=None, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info.value)

    # PUT Request 
    httpx_mock.add_exception(httpx.ConnectError(message=error_message), method = "PUT", url= url )

    with pytest.raises(Exception) as exc_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info.value)

@pytest.mark.asyncio
async def test_request_hostname_error(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://invalid_hostname/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Hostname error occurred."

    httpx_mock.add_exception(httpx.RequestError("Failed to resolve hostname"), method="PUT", url=url)

    with pytest.raises(httpx.RequestError) as exc_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)


    assert error_message in str(exc_info.value)


@pytest.mark.asyncio
async def test_unauthorised_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None: 

    url = "http://example.com/api"
    model = MockRequestModel(foo = "yeh")
    json_body = py_to_dict(model)
    params = {"key": "value"}
    final_url = httpx.URL(url, params = {"key": "value"})
    error_message = "Unauthorised access"

    # POST request with unauthorized exception
    httpx_mock.add_response(method="POST", url=url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_post_request(client=client_service, url=url, json_body=json_body, params=None, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # PUT request with unauthorized exception
    httpx_mock.add_response(method="PUT", url=url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_put_request(client=client_service, url=url, json_body=json_body, params=None, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # GET request with unauthorized exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # DELETE request with unauthorized exception
    httpx_mock.add_response(method="DELETE", url=url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)


@pytest.mark.asyncio
async def test_bad_request_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    
    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Bad request"

    # GET request with bad request exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # POST request with bad request exception
    httpx_mock.add_response(method="POST", url=url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # PUT request with bad request exception
    httpx_mock.add_response(method="PUT", url=url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # DELETE request with bad request exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)


@pytest.mark.asyncio
async def test_http_validation_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    
    # GET request with HTTP validation exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=422)
    with pytest.raises(HTTPValidationException):
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message="")

    # POST request with HTTP validation exception
    httpx_mock.add_response(method="POST", url=url, status_code=422)
    with pytest.raises(HTTPValidationException):
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="")

    # PUT request with HTTP validation exception
    httpx_mock.add_response(method="PUT", url=url, status_code=422)
    with pytest.raises(HTTPValidationException):
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="")

    # DELETE request with HTTP validation exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=422)
    with pytest.raises(HTTPValidationException):
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message="")

@pytest.mark.asyncio
async def test_internal_server_error_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Internal server error"

    # GET request with server error exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # POST request with server error exception
    httpx_mock.add_response(method="POST", url=url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # PUT request with server error exception
    httpx_mock.add_response(method="PUT", url=url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)

    # DELETE request with server error exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value)



"""Standard Model Response and Status Response Model Testing"""

# Test successful GET request with standard model
@pytest.mark.asyncio
async def test_successful_get_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    response_model = MockResponseModel(bar = "example_return_value")
                                        
    httpx_mock.add_response(method="GET", url=final_url, status_code=200)

    result = await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model

# Test successful GET request with StatusResponse
@pytest.mark.asyncio
async def test_successful_get_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    response_model = StatusResponse(status=Status(success=True, details="GET request completed successfully"))

    httpx_mock.add_response(method="GET", url=final_url, json=response_model.dict(), status_code=200)

    result = await parsed_get_request(client=client_service, url=url, params=params, model=StatusResponse, error_message="Error occurred")
    assert result == response_model


#Test successful POST request with standard model
@pytest.mark.asyncio
async def test_post_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = {"foo": "example_value"}
    response_model = MockResponseModel(bar="example_value")

    httpx_mock.add_response(method="POST", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model

# Test successful POST request with StatusResponse
@pytest.mark.asyncio
async def test_post_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = {"foo": "example_value"}
    response_model = StatusResponse(status=Status(success=True, details="POST request completed successfully"))

    httpx_mock.add_response(method="POST", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message="Error occurred")
    assert result == response_model

# Test failed POST request with StatusResponse.
@pytest.mark.asyncio
async def test_failed_post_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo= "mocked-request"))
    error_message = "Error occurred"

    response_model = StatusResponse(status=Status(success=False, details="POST request did not complete successfully"))

    httpx_mock.add_response(method="POST", url=url, json=response_model.dict(), status_code=200)
    
    with pytest.raises(Exception) as exc_info:
        await parsed_put_request_with_status(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message=error_message)
    
    assert error_message in str(exc_info.value)
    assert "Status object from API indicated failure" in str(exc_info.value)


#Test successful PUT request with standard model
@pytest.mark.asyncio
async def test_successful_put_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo = "mocked-request"))
    response_model = MockResponseModel(bar="example_value")

    httpx_mock.add_response(method="PUT", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model

# Test successful PUT request with StatusResponse
@pytest.mark.asyncio
async def test_successful_put_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo = "mocked-request"))
    response_model = StatusResponse(status=Status(success=True, details="PUT request completed successfully"))

    httpx_mock.add_response(method="PUT", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_put_request_with_status(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message="Error occurred")
    assert result == response_model

# Test failed PUT request with StatusResponse
@pytest.mark.asyncio
async def test_failed_put_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo = "mocked-request"))
    error_message = "Error occurred"
    
    response_model = StatusResponse(status=Status(success=False, details="PUT request did not complete successfully"))

    httpx_mock.add_response(method="PUT", url=url, json=response_model.dict(), status_code=200)

    with pytest.raises(Exception) as exc_info:
        await parsed_put_request_with_status(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message=error_message)
    
    assert error_message in str(exc_info.value)
    assert "Status object from API indicated failure" in str(exc_info.value)

# Test successful DELETE request with standard model.
@pytest.mark.asyncio
async def test_successful_delete_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    response_model = MockResponseModel(bar="example_value")

    httpx_mock.add_response(method="DELETE", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_delete_request(client=client_service, url=url, params=None, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model

# Test successful DELETE request with StatusResponse
@pytest.mark.asyncio
async def test_successful_delete_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    response_model = StatusResponse(status=Status(success=True, details="DELETE request completed successfully"))

    httpx_mock.add_response(method="DELETE", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_delete_request_with_status(client=client_service, url=url, params=None, model=StatusResponse, error_message="Error occurred")
    assert result == response_model

# Test failed DELETE request with StatusResponse
@pytest.mark.asyncio
async def test_failed_delete_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    error_message = "Error occurred"
    
    response_model = StatusResponse(status=Status(success=False, details="DELETE request did not complete successfully"))

    httpx_mock.add_response(method="DELETE", url=url, json=response_model.dict(), status_code=200)

    with pytest.raises(Exception) as exc_info:
        await parsed_delete_request_with_status(client=client_service, url=url, params=None, model=StatusResponse, error_message=error_message)
    
    assert error_message in str(exc_info.value)
    assert "Status object from API indicated failure" in str(exc_info.value)


"""Unsuccessful model parsing for POST Requests"""

@pytest.mark.asyncio
async def test_post_request_missing_required_field(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model: dict = {}  # Missing required field
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(Exception) as exc_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info)

@pytest.mark.asyncio
async def test_post_request_incorrect_data_format(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model = {"bar": [1, 2, 3]}  # Incorrect type
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(Exception) as exc_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info)

@pytest.mark.asyncio
async def test_post_request_null_or_none(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model = None 
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(ValidationException) as exc_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert "JSON parsing failed" in str(exc_info)


@pytest.mark.asyncio
async def test_put_request_incorrect_data_type(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model = {"bar": None}  # None type
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(Exception) as exc_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exc_info)

    


