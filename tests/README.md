## Provena Client Library Testing Documentation

### 1. Unit Tests

#### 1.1 Real HTTP/Server Tests - (JSONPlaceHolder) - L1 Layer
The JSONPlaceholder tests validate that the `HttpClient` (Custom class wrapping `httpx`) methods handle real API interactions correctly. These tests include scenarios for GET, POST, PUT, and DELETE requests, ensuring the client sends requests with the correct URLs, headers, and payloads, and correctly handles different types of responses, including successful responses and various error conditions (e.g., 401 Unauthorized, 422 Unprocessable Entity).

#### 1.2 Mock Testing - L1 Layer
Mock Testing uses mock objects (`httpx_mock`) to simulate real API interactions, allowing for comprehensive testing of the `HttpClient` (Custom class wrapping `httpx`) methods without actual server dependencies. Key tests include handling connection errors, hostname resolution errors, unauthorized (401) responses, bad request (400) responses, validation errors (422), and internal server errors (500). These tests ensure the client library is robust and can gracefully handle various error conditions.

#### 1.3 Mock Testing - L2 Layer

The unit tests within this layer focused solely on the client library's helper methods ([Client Library API Helper Methods](https://github.com/provena/provena-python-client/blob/main/src/provenaclient/clients/client_helpers.py)) which are high level methods that call underlying HTTP request methods (GET, PUT, POST, DELETE) as all client library functions making any API calls utilised these methods, hence covering all scenarios.

This allowed us to test those respective methods were working as expected and assess that the parsing functionality of JSON to a python datatype is also working correctly as expected. 

### 2. Integration Tests
The integration tests were designed to assess various functionalities of the Client Library and ensure that they are working as expected within the Provena System. The tests covered various scenarios such as:

1. Creating & Registering Datasets.
2. Searching newly created entities (Datasets, Agents (Person, Organisation), Models, Study, etc.).
3. Fetching Items (Pagination & Non-Pagination Listing) and assessing whether items created as a part of the test are correctly present within the list.
4. Launching Model Runs - Testing the whole provenance lifecycle from a client library perspective.

### 3. How to Run Unit and Integration Tests

#### 3.1 Unit Tests:
1. Install all Poetry dependencies located within `pyproject.toml`.
2. Navigate to the test folder.
3. Run the command `pytest test_unit.py`.

#### 3.2 Integration Tests:
1. Install all Poetry dependencies located within `pyproject.toml`.
2. Source the ADMIN_OFFLINE_TOKEN of a dev-test-integration bot. Please ask someone from the Provena Development Team and they can guide you on this. Please don't use your own user, as your user-link maybe removed. 
3. Create a `.env` file within the test folder with the following format (Replace * with your relevant info):
    ```env
    DOMAIN=***
    REALM_NAME=***
    PROVENA_ADMIN_OFFLINE_TOKEN=***
    CLIENT_ID=automated-access
    ```
4. Navigate to the test folder.
5. Run the command `pytest test_integration.py`.
