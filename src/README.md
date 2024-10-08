# Provena Client Architecture Description. 

The Provena Python Client is built using a layered architecture that abstracts API interactions into a modular and user-friendly experience. It consists of three main layers: 
 - An HTTP Client Wrapper for handling asynchronous requests.
 - Client interfaces that are responsible for preparing API requests and parsing API responses to interactive python datatypes. 
 - User interface modules that provide a simple and straight forward interface for the users to interact with.

This design enables modularity, flexibility and ease of maintenance, enhancing the developer and contribution experience while keeping the complexities hidden from the user. 


## Software Architecture and Design:

### Overview 
The Provena Python Client uses a "layered architecture" that is supported by the Dependency Injection pattern, providing an approach that is modular and allows us to have a separation of concerns. 

For a visual diagram of one of the functionalities provided by the Provena Python Client, refer to this [example of dataset fetch](./fetch-dataset-flow.svg).

<hr>

### Layered Architecture Description (Tiered Approach):

1. **Layer 1 (L1 - HTTP Client Wrapper):**

    - **Purpose**: This L1 layer serves as the foundational layer that wraps/encapsulates around an HTTP client, specifically `httpx` for Provena Python Client. This layer allows us to abstract the direct handling of HTTP methods (GET, PUT, POST, DELETE) and centralises certain HTTP client settings such as timeouts. Furthermore, having this separate HTTP layer provides us with an option to replace the underlying HTTP library in the future without affecting the rest of the client library

    - **Current Approach**: In the current implementation of Layer 1 (L1 - HTTP Client Wrapper) within the Provena Python Client, we use the `httpx` library to handle HTTP requests in an **asynchronous fashion**. This allows for better performance of the client and allows for non-blocking requests. Furthermore, each HTTP methods in our client - GET, PUT, POST, DELETE -- is designed to accept and handle the necessary parameters such as auth, headers, query params, and other body params in accordance to the Provena API requirements. In the current approach, `httpx`, is used within a context-manager which ensures that each API request is handled in a fresh session, maintaining clean and reliable session management throughout API interactions.
    
<hr>

2. **Layer 2 (L2 - Client Interfaces):** 
    - **Purpose:** This L2 layer serves and sits between the HTTP client wrapper (Layer 1) and the user interface module (Layer 3). It's responsible for preparing the API request payload and parsing API responses to interactive Python datatype. This layer helps us simplify and streamline the process of constructing the API requests and parsing responses within the Provena Python Client. Additionally, it enables abstraction of the complexity involved in API request handling, providing a simpler interface for the downstream layer (L3). The data parsing and validation performed by L2 ensures all responses conform to the expected types, preventing users from interacting with invalid interactive Python datatypes.

    - **Current Approach:** The current implementation of Layer 2 (L2 - Client Interfaces) it leverages the authentication and configuration settings that are provided by the user to securely and effectively manage the API communications. Furthermore, each API within this layer has its dedicated client that encapsulates specific business logic and functionalities relevant to that respective API. 

      Currently, the L2 layer responsibilities include constructing and preparing the API request payload based on the respective API and endpoint (a defined function within the client) requirements and the payload is sent through to the HTTP Client provided by L1 through the methods of `parsed_get_request_with_status`, `parsed_get_request`, `parsed_post_request`, etc. Additionally, the L2 layer is responsible for parsing and validating the API responses returned from L1 against Pydantic models sourced from the Provena Interfaces into structured and interactive Python datatypes if successful, else it handles and raises its custom exceptions accordingly.

    
<hr>

3. **Layer 3 (L3 - User Interface Modules):** 
    - **Purpose:** This L3 layer serves as the topmost layer in the Provena Python Client architecture, that is directly interacted by the end-user using the Provena Python Client. This layer is responsible for providing a simple and user-friendly interface to the underlying API functionalities defined and created in Layer 2. This layer only presents users with a set of functions that are revealed based on the chosen API the user decides to interact with and allows to them to perform operations without having to worry and managing the API lifecycle. This layer simplifies the user experience by providing a clear and accessible interface to complex backend functionalities. This design not only enhances ease of use but also ensures that changes to the Provena Python client can be managed without significantly changing or affecting the end-user’s interaction. 

    - **Current Approach:** In the current implementation of Layer 3 (L3 - User Interface Modules), comprises of various modules, each corresponding to an API of Provena and encapsulating related functionalities. All of these modules, along with the corresponding L2 clients that manage direct API interactions, are instantiated within a single class, ProvenaClient. This class serves as the entry point for end-users to access all client functionalities. Dependency injection is heavily utilised here, as the ProvenaClient class injects the modules of auth, config, and the respective API clients into each module's constructor. This setup ensures that each module has access to shared interfaces such as auth and config, and allows us to change those shared interfaces independently without altering the user-facing module's functionality.

## Directory Structure Overview: 

After understanding the directory structure, it's essential to see how these layers map to the directory structure. Most of the directories are organised in a way to reflect the Provena Python Client architecture as described previously, and each one of them play a specific role in implementing the Provena Python Client functionality. 

- **provenaclient/auth**: This directory contains the interfaces and helper functions supporting the authentication flows used by Provena Python Client of which there a two. A device flow (for manual human authentication) and an offline flow (for automated or scheduled tasks). This directory also includes a logger configured to track authentication-related requests and responses. Furthermore, helper functions within this directory handle tasks like token storage, expiry, and renewal validation, etc.
 
- **provenaclient/clients (L2)**: This directory contains the client interfaces for various API's that the Provena Client interacts with on behalf of the user. It includes separate modules for each Provena microservice such as `auth`, `datastore`, `job-api`, `prov-api`, `search-api`, `registry-api`, and `id-service-api`. Each module contains unique functions that facilitate API calls to the respective hosted API.
 
- **provenaclient/models**: This directory contains custom Pydantic models that are currently not present in [ProvenaInterfaces](https://pypi.org/project/provena-interfaces/) but are still required within the Client Library. 

- **provenaclient/module (L3)**: This directory contains various modules that serve as the user-facing layer of the Provena Python Client. Each module represents an individual API, such as auth, datastore, registry, etc. These modules directly interact with the specific client modules in the provenaclient/clients directory, based on their API mapping (e.g., datastore module -> datastore client), which facilitates API calls to the respective hosted services. Furthermore, within nearly all modules in the provenaclient/modules directory, some submodules are instantiated within the module, managing specific functionalities related to the API (e.g., admin, IO).

- **provenaclient/utils (L1)** - This directory contains utility interfaces and helper functions that support the Provena Python Client such as custom exception class, and configuration class. This directory also includes the custom `httpx` client that is encapsulated in an `HttpxClient` class. This class includes custom functions that wrap around the httpx HTTP methods, allowing easy integration and standardisation across the client library.
        
    