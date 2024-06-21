'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: Helper methods for clients namely a standard interface ClientService along with reusable patterns to interact with the HTTPX L1 Layer
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Just noting I think we could streamline the helper functions a bit
'''

from abc import ABC
from provenaclient.auth import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.helpers import *
from provenaclient.utils.http_client import HttpClient
from typing import Dict, Mapping, Optional
from provenaclient.utils.exceptions import CustomTimeoutException


class ClientService(ABC):
    """
    This class interface just captures that the client has an instantiated auth
    manager which allows for helper functions abstracted for L2 clients.
    """
    _auth: AuthManager
    _config: Config


async def parsed_get_request_with_status(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes get request
    - checks status/http codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make GET request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_get_request(url=url, params=filtered_params, auth=get_auth())
        data = handle_response_with_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_get_request(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes get request
    - checks http codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make GET request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_get_request(url=url, params=filtered_params, auth=get_auth())
        data = handle_response_non_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_post_request(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes POST request
    - checks http codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make POST request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON
        json_body: Optional[JsonData]: JSON data to post if any

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_post_request(url=url, data=json_body, params=filtered_params, auth=get_auth())
        data = handle_response_non_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data

async def parsed_post_request_with_status(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str, model: Type[BaseModelType], files: Optional[HttpxFileUpload] = None) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes POST request
    - checks http/status codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make POST request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON
        json_body: Optional[JsonData]: JSON data to post if any
        files: Optional[HttpxFileUpload]: A dictionary representing file(s) to be uploaded with the
               request. Each key in the dictionary is the name of the form field for the file according,
               to API specifications. For Provena it's "csv_file" and and the value 
               is a tuple of (filename, filedata, MIME type or media type).

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_post_request(url=url, data=json_body, params=filtered_params, files = files, auth=get_auth())
        data = handle_response_with_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_delete_request_with_status(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes DELETE request
    - checks http/status codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make POST request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON
        json_body: Optional[JsonData]: JSON data to post if any

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_delete_request(url=url, params=filtered_params, auth=get_auth())
        data = handle_response_with_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_delete_request(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes DELETE request
    - checks http/status codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make POST request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON
        json_body: Optional[JsonData]: JSON data to post if any

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_delete_request(url=url, params=filtered_params, auth=get_auth())
        data = handle_response_non_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_put_request(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes put request
    - checks http codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make put request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON
        json_body: Optional[JsonData]: JSON data to put if any

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_put_request(url=url, data=json_body, params=filtered_params, auth=get_auth())
        data = handle_response_non_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_put_request_with_status(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes put request
    - checks http/status codes
    - parses model etc

    Returns the parsed validated, safe to use 200OK model result

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make put request to
        error_message (str): The error message to embed in other exceptions
        model (Type[BaseModelType]): Model to parse for response JSON
        json_body: Optional[JsonData]: JSON data to put if any

    Raises:
        e: Exception depending on error

    Returns:
        BaseModelType: The specified parsed model
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_put_request(url=url, data=json_body, params=filtered_params, auth=get_auth())
        data = handle_response_with_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data



async def validated_get_request(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], url: str, error_message: str) -> Response:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes get request
    - checks http codes

    This method does not do any base model parsing and only checks HTTP status codes.

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make GET request to
        error_message (str): The error message to embed in other exceptions

    Raises:
        e: Exception depending on error

    Returns:
        None
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_get_request(url=url, params=filtered_params, auth=get_auth())
        
        handle_err_codes(
            response=response,
            error_message=error_message
        )

        return response

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e


async def parsed_post_request_none_return(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str) -> None:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes POST request
    - checks http codes

    This method does not do any base model parsing and only checks HTTP status codes.

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make POST request to
        error_message (str): The error message to embed in other exceptions
        json_body: Optional[JsonData]: JSON data to post if any

    Raises:
        e: Exception depending on error

    Returns:
        None
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_post_request(url=url, data=json_body, params=filtered_params, auth=get_auth())
        
        handle_err_codes(
            response=response,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e
    

async def parsed_delete_request_non_return(client: ClientService, params: Optional[Mapping[str, Optional[ParamTypes]]], url: str, error_message: str) -> None:
    """

    High level helper function which 

    - gets the auth
    - builds the filtered param list
    - makes DELETE request
    - checks http/status codes

    This method does not do any base model parsing and only checks HTTP status codes.

    Args:
        client (ClientService): The client being used. Relies on client interface.
        params (Optional[Mapping[str, Optional[ParamTypes]]]): The params if any
        url (str): The url to make POST request to
        error_message (str): The error message to embed in other exceptions

    Raises:
        e: Exception depending on error

    Returns:
        None
    """
    # Prepare and setup the API request.
    get_auth = client._auth.get_auth  # Get bearer auth
    filtered_params = build_params_exclude_none(params if params else {})

    try:
        response = await HttpClient.make_delete_request(url=url, params=filtered_params, auth=get_auth())
        
        handle_err_codes(
            response=response,
            error_message=error_message
        )

    except BaseException as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e
