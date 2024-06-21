'''
Created Date: Friday June 19st 2024 +0000
Author: Parth Kulkarni
-----
Last Modified: Friday June 21st 2024 12:40:49 pm +0000
Modified By: Parth Kulkarni
-----
Description: Unit testing of client library through L1 and L2 Layer. 
             Also contains small number of integration tests with real 
             REST API server (JSONPlaceHolder)
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
21-06-2024 | Parth Kulkarni | Completion of Unit Tests With Doc String and Comments.

'''




from provenaclient.clients.client_helpers import parsed_delete_request, parsed_delete_request_with_status, parsed_get_request, parsed_get_request_with_status, parsed_post_request, parsed_post_request_with_status, parsed_put_request, parsed_put_request_with_status
from provenaclient.utils.helpers import py_to_dict
from provenaclient.utils.http_client import HttpClient, HttpxBearerAuth
from provenaclient.utils.exceptions import AuthException, BadRequestException, CustomTimeoutException, HTTPValidationException, ServerException, ValidationException
from ProvenaInterfaces.SharedTypes import StatusResponse, Status
from unit_helpers import MockedClientService, MockedAuthService, MockRequestModel, MockResponseModel, is_exception_in_chain
from provenaclient.utils.config import Config

import pytest
import httpx
from pytest_httpx import HTTPXMock
import json
from pydantic import ValidationError

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

"""L2 Layer Testing"""

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


@pytest.mark.asyncio
async def test_request_connect_error(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests handling of connection errors across different HTTP methods.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Connection error has occurred."

    # GET Request. 
    httpx_mock.add_exception(httpx.ConnectError(message="Failed to connect."), method = "GET", url= url )
    
    with pytest.raises(Exception) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=None, model=MockResponseModel, error_message=error_message)
    assert is_exception_in_chain(exec_info.value, httpx.ConnectError), "httpx.ConnectError not found in exception chain"
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."

    # POST Request
    httpx_mock.add_exception(httpx.ConnectError(message=error_message), method = "POST", url= url )

    with pytest.raises(Exception) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert is_exception_in_chain(exec_info.value, httpx.ConnectError), "httpx.ConnectError not found in exception chain"
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."

    # DELETE Request
    httpx_mock.add_exception(httpx.ConnectError(message=error_message), method = "DELETE", url= url )

    with pytest.raises(Exception) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=None, model=MockResponseModel, error_message=error_message)
    assert is_exception_in_chain(exec_info.value, httpx.ConnectError), "httpx.ConnectError not found in exception chain"
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."

    # PUT Request 
    httpx_mock.add_exception(httpx.ConnectError(message=error_message), method = "PUT", url= url )

    with pytest.raises(Exception) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert is_exception_in_chain(exec_info.value, httpx.ConnectError), "httpx.ConnectError not found in exception chain"
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."

@pytest.mark.asyncio
async def test_request_hostname_error(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests error handling when an invalid hostname is used in a PUT request.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://invalid_hostname/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Hostname error occurred."

    httpx_mock.add_exception(httpx.RequestError("Failed to resolve hostname"), method="PUT", url=url)

    with pytest.raises(Exception) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    
    assert is_exception_in_chain(exec_info.value, httpx.RequestError), "httpx.RequestError not found in exception chain"
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."

@pytest.mark.asyncio
async def test_unauthorised_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None: 
    """Tests the handling of unauthorized (401) responses across various HTTP methods.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

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
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Auth Exception."

    # PUT request with unauthorized exception
    httpx_mock.add_response(method="PUT", url=url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_put_request(client=client_service, url=url, json_body=json_body, params=None, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Auth Exception."

    # GET request with unauthorized exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Auth Exception."

    # DELETE request with unauthorized exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=401)
    with pytest.raises(AuthException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Auth Exception."


@pytest.mark.asyncio
async def test_bad_request_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests the handling of bad request (400) responses across various HTTP methods.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Bad request"

    # GET request with bad request exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Bad Request Exception."

    # POST request with bad request exception
    httpx_mock.add_response(method="POST", url=url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Bad Request Exception."

    # PUT request with bad request exception
    httpx_mock.add_response(method="PUT", url=url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Bad Request Exception."

    # DELETE request with bad request exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=400)
    with pytest.raises(BadRequestException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Bad Request Exception."


@pytest.mark.asyncio
async def test_http_validation_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests the handling of validation errors (422) across various HTTP methods.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "HTTP Validation Failed."
    
    # GET request with HTTP validation exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=422)
    with pytest.raises(HTTPValidationException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Validation Exception."


    # POST request with HTTP validation exception
    httpx_mock.add_response(method="POST", url=url, status_code=422)
    with pytest.raises(HTTPValidationException) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
        assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Validation Exception."


    # PUT request with HTTP validation exception
    httpx_mock.add_response(method="PUT", url=url, status_code=422)
    with pytest.raises(HTTPValidationException) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Validation Exception."

    # DELETE request with HTTP validation exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=422)
    with pytest.raises(HTTPValidationException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Validation Exception."

@pytest.mark.asyncio
async def test_internal_server_error_exception(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests the handling of validation errors (422) across various HTTP methods.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    error_message = "Internal server error"

    # GET request with server error exception
    httpx_mock.add_response(method="GET", url=final_url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Server Exception."

    # POST request with server error exception
    httpx_mock.add_response(method="POST", url=url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Server Exception."

    # PUT request with server error exception
    httpx_mock.add_response(method="PUT", url=url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Server Exception."

    # DELETE request with server error exception
    httpx_mock.add_response(method="DELETE", url=final_url, status_code=500)
    with pytest.raises(ServerException) as exec_info:
        await parsed_delete_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in HTTP Server Exception."



"""Standard Model Response and Status Response Model Testing"""

# Test successful GET request with standard model
@pytest.mark.asyncio
async def test_successful_get_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful GET requests to ensure that the standard response model is returned and correctly parsed as expected.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    response_model = MockResponseModel(bar = "example_return_value")
    response_model_two = MockResponseModel(bar = "different_return_value")

    httpx_mock.add_response(method="GET", url=final_url, json= response_model.dict(), status_code=200)

    result = await parsed_get_request(client=client_service, url=url, params=params, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."

# Test successful GET request with StatusResponse
@pytest.mark.asyncio
async def test_successful_get_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful GET requests with a specific status response model for correct data handling.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    params = {"key": "value"}
    final_url = httpx.URL(url, params = params)
    response_model = StatusResponse(status=Status(success=True, details="GET request completed successfully"))
    response_model_two = StatusResponse(status=Status(success=True, details="GET request completed differently but successfully."))


    httpx_mock.add_response(method="GET", url=final_url, json=response_model.dict(), status_code=200)

    result = await parsed_get_request_with_status(client=client_service, url=url, params=params, model=StatusResponse, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."


#Test successful POST request with standard model
@pytest.mark.asyncio
async def test_post_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    url = "http://example.com/api"
    json_body = {"foo": "example_value"}
    response_model = MockResponseModel(bar="example_value")
    response_model_two = MockResponseModel(bar = "different_return_value")


    httpx_mock.add_response(method="POST", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."

# Test successful POST request with StatusResponse
@pytest.mark.asyncio
async def test_post_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful POST requests by verifying correct handling and parsing of a StatusResponse model indicating a successful request.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = {"foo": "example_value"}
    response_model = StatusResponse(status=Status(success=True, details="POST request completed successfully"))
    response_model_two = StatusResponse(status=Status(success=True, details="POST request completed differently but successfully."))

    httpx_mock.add_response(method="POST", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."


# Test failed POST request with StatusResponse.
@pytest.mark.asyncio
async def test_failed_post_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests handling of failed POST requests by simulating a scenario where the server indicates a failure in the StatusResponse model.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """


    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo= "mocked-request"))
    error_message = "Error occurred with POST Request"
    response_model = StatusResponse(status=Status(success=False, details="POST request did not complete successfully"))

    httpx_mock.add_response(method="POST", url=url, json=response_model.dict(), status_code=200)
    
    with pytest.raises(Exception) as exec_info:
        await parsed_post_request_with_status(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message=error_message)
    
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."
    assert "Status object from API indicated failure" in str(exec_info.value), \
        "The exception message did not contain the expected 'Status object from API indicated failure' text, indicating a mismatch in the error handling."

#Test successful PUT request with standard model
@pytest.mark.asyncio
async def test_successful_put_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful PUT requests to ensure that the standard response model is returned and correctly parsed as expected.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo = "mocked-request"))
    response_model = MockResponseModel(bar="example_value")
    response_model_two = MockResponseModel(bar = "different_return_value")

    httpx_mock.add_response(method="PUT", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_put_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."

# Test successful PUT request with StatusResponse
@pytest.mark.asyncio
async def test_successful_put_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful PUT requests by verifying correct handling and parsing of a StatusResponse model indicating a successful request.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo = "mocked-request"))
    response_model = StatusResponse(status=Status(success=True, details="PUT request completed successfully"))
    response_model_two = StatusResponse(status=Status(success=True, details="PUT request completed differently but successfully."))


    httpx_mock.add_response(method="PUT", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_put_request_with_status(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."

# Test failed PUT request with StatusResponse
@pytest.mark.asyncio
async def test_failed_put_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests handling of failed PUT requests by simulating a scenario where the server indicates a failure in the StatusResponse model."""
    
    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo = "mocked-request"))
    error_message = "Error occurred in PUT Request"
    response_model = StatusResponse(status=Status(success=False, details="PUT request did not complete successfully"))

    httpx_mock.add_response(method="PUT", url=url, json=response_model.dict(), status_code=200)

    with pytest.raises(Exception) as exec_info:
        await parsed_put_request_with_status(client=client_service, url=url, params=None, json_body=json_body, model=StatusResponse, error_message=error_message)
    
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."
    assert "Status object from API indicated failure" in str(exec_info.value), \
        "The exception message did not contain the expected 'Status object from API indicated failure' text, indicating a mismatch in the error handling."


# Test successful DELETE request with standard model.
@pytest.mark.asyncio
async def test_successful_delete_request_standard_model(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful DELETE requests to ensure that the standard response model is returned and correctly parsed as expected.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    response_model = MockResponseModel(bar="example_value")
    response_model_two = MockResponseModel(bar = "different_return_value")

    httpx_mock.add_response(method="DELETE", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_delete_request(client=client_service, url=url, params=None, model=MockResponseModel, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."

# Test successful DELETE request with StatusResponse
@pytest.mark.asyncio
async def test_successful_delete_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests successful DELETE requests by verifying correct handling and parsing of a StatusResponse model indicating a successful request.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """
    url = "http://example.com/api"
    response_model = StatusResponse(status=Status(success=True, details="DELETE request completed successfully"))
    response_model_two = StatusResponse(status=Status(success=True, details="DELETE request completed differently but successfully."))

    httpx_mock.add_response(method="DELETE", url=url, json=response_model.dict(), status_code=200)

    result = await parsed_delete_request_with_status(client=client_service, url=url, params=None, model=StatusResponse, error_message="Error occurred")
    assert result == response_model, "The response does not match the expected response model."
    assert result != response_model_two, "The response incorrectly matches an unintended response model."

# Test failed DELETE request with StatusResponse
@pytest.mark.asyncio
async def test_failed_delete_request_status_response(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests handling of DELETE POST requests by simulating a scenario where the server indicates a failure in the StatusResponse model.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    error_message = "Error occurred"
    response_model = StatusResponse(status=Status(success=False, details="DELETE request did not complete successfully"))

    httpx_mock.add_response(method="DELETE", url=url, json=response_model.dict(), status_code=200)

    with pytest.raises(Exception) as exec_info:
        await parsed_delete_request_with_status(client=client_service, url=url, params=None, model=StatusResponse, error_message=error_message)
    
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."
    assert "Status object from API indicated failure" in str(exec_info.value), \
        "The exception message did not contain the expected 'Status object from API indicated failure' text, indicating a mismatch in the error handling."



"""Unsuccessful model parsing for POST Requests/Response"""

@pytest.mark.asyncio
async def test_post_request_missing_required_field(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests POST request response with missing required fields to verify error handling and validation working as expected.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model: dict = {}  # Missing field
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(Exception) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    
    assert is_exception_in_chain(exec_info.value, ValidationError), "Pydantic ValidationError not found in exception chain."
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."


@pytest.mark.asyncio
async def test_post_request_incorrect_data_format(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests POST request response with incorrect field for model to ensure that validation and error handling is working correctly.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """


    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model = {"bar": [1, 2, 3]}  # Incorrect type
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(Exception) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    
    assert is_exception_in_chain(exec_info.value, ValidationError), "Pydantic ValidationError not found in exception chain."
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."


@pytest.mark.asyncio
async def test_post_request_null_or_none(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests POST request where the response model is null or none, to check error handling for scenarios where no data is returned.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model = None 

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

   # The custom error message is not captured by the parsing JSON Method, hence generic error message provided.
    with pytest.raises(ValidationException) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message="Error occured")

    assert "JSON parsing failed" in str(exec_info), \
    "The exception message did not contain the expected 'JSON parsing failed' text, suggesting that the error handling for JSON parsing issues may not be functioning correctly."


@pytest.mark.asyncio
async def test_put_request_incorrect_data_type(httpx_mock: HTTPXMock, client_service: MockedClientService) -> None:
    """Tests PUT requests response with None/null response in a returned field.

    Parameters
    ----------
    httpx_mock : HTTPXMock
        The mock for HTTPX requests to simulate server responses.
    client_service : MockedClientService
        The mocked client service used to make HTTP requests.
    """

    url = "http://example.com/api"
    json_body = py_to_dict(MockRequestModel(foo="mocked-request"))
    response_model = {"bar": None}  # None type
    error_message = "Error occurred Validating Model"

    httpx_mock.add_response(method="POST", url=url, json=response_model, status_code=200)

    with pytest.raises(Exception) as exec_info:
        await parsed_post_request(client=client_service, url=url, params=None, json_body=json_body, model=MockResponseModel, error_message=error_message)
    assert error_message in str(exec_info.value), f"Error message: {error_message} not found in Exception."
    
