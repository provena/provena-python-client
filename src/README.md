# Provena Client Architecture Description. 

## Folder Description: 

- provenaclient/auth: This directory contains the interfaces and helper functions supporting the authentication flow used by Provena Python Client, including device flow and offline flow. This directory also includes a logger that is specifically configured for tracking authentication related requests and responses. Furthermore, helper functions within this directory handle tasks like token storage, expiry and renewal validation etc.
 
- provenaclient/clients: This directory contains the client interfaces for various API's that the Provena Client interacts with. It includes seperate modules for each Provena microservice such as `auth`, `datastore`, `job-api`, `prov-api`, `search-api`, `registry-api`, and `id-service-api`. Each module contains unique functions that facilitate API calls to the respective hosted api.
 
- provenaclient/models: This directory contains Pydantic models that are currently not present in ProvenaInterfaces[https://pypi.org/project/provena-interfaces/] but are still required within the Client Library. 

- provenaclient/module: This directory contains various modules that serve as the user-facing layer of the Provena Python Client. Each module represents an individual API, such as auth, datastore, registry, etc. These modules directly interact with the specific client modules in the provenaclient/clients directory, based on their API mapping (e.g., datastore module -> datastore client), which facilitates API calls to the respective hosted services. Furthermore, within nearly all modules in the provenaclient/modules directory, there are submodules that are instantiated within the module, managing specific functionalities related to the API (e.g., admin, IO).

- provenaclient/utils - This directory contains utility interfaces and helper functions that support the Provena Python Client such as custom exception class, configuration class. This directory also contains the custom `httpx` client that is encapsulated in an `HttpxClient` class. This class includes custom functions that wrap around the httpx HTTP methods, allowing easy integration and standardisation across the client library.

## Software Architecture Description:

### Overview 
The Provena Python Client uses a "layered architecture" that is supported by the Dependency Injection pattern, providing an approach that is modular and allows us to have a separation of concerns. 

### Layered Architecture Description (Tiered Approach):   

1. Layer 1 (L1 - HTTP Client Wrapper):
    - Purpose: This L1 layer serves as the foundational layer that wraps/encapsulates around a HTTP client, specifically `httpx` for Provena Python Client.This layer allows us to abstract the direct handling of HTTP methods (GET,PUT,POST,DELETE) and centralises certain HTTP client settings such as timeouts.

    - Current Approach: In the current implementation of Layer 1 (L1 - HTTP Client Wrapper) within the Provena Python Client, we use the `httpx` library to handle HTTP requests in an **asynchronous fashion**. This allows for better performance of the client and allows for non-blocking requests. Furthermore, each HTTP methods in our client - GET,PUT,POST,DELETE -- is designed to accept and handle the necessary parameters such as auth,headers, query params, and other body params in accordance to the Provena API requirements. 

    In the current approach, `httpx`, is used within a context-manager which ensures that each API request is handled in a fresh session, maintaining clean and reliable session management throughout API interactions.

    - Benefit: The benefit of having this separate HTTP layer is that it provides us with an option to replace the underlying HTTP library in the future without affecting rest of the client library. 

2. Layer 2 (L2 - Client Interfaces): 
    - Purpose: This L2 layer serves and sits between the HTTP client wrapper and the user interface module. It's responsible for preparing the API request payload and parsing API responses to python datatypes. This layer helps us simplify the 
    - Current Approach:
    - Benefit:

3. Layer 3 (L3 - User Interface Modules): 
    - Purpose: 
    - Current Approach: 
    - Benefit: 