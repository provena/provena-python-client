from abc import ABC
from provenaclient.auth import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.helpers import *
from provenaclient.utils.http_client import HttpClient
from typing import Dict, Optional


class ClientService(ABC):
    """
    This class interface just captures that the client has an instantiated auth
    manager which allows for helper functions abstracted for L2 clients.
    """
    _auth: AuthManager
    _config: Config


async def parsed_get_request_with_status(client: ClientService, params: Optional[Dict[str, Optional[ParamTypes]]], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
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
        params (Optional[Dict[str, Optional[ParamTypes]]]): The params if any
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

    except api_exceptions as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data


async def parsed_get_request(client: ClientService, params: Optional[Dict[str, Optional[ParamTypes]]], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
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
        params (Optional[Dict[str, Optional[ParamTypes]]]): The params if any
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
        

    except api_exceptions as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data

async def parsed_post_request(client: ClientService, params: Optional[Dict[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
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
        params (Optional[Dict[str, Optional[ParamTypes]]]): The params if any
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
        response = await HttpClient.make_post_request(url=url,data=json_body, params=filtered_params, auth=get_auth())
        data = handle_response_non_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except api_exceptions as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data

async def parsed_post_request_with_status(client: ClientService, params: Optional[Dict[str, Optional[ParamTypes]]], json_body: Optional[JsonData], url: str, error_message: str, model: Type[BaseModelType]) -> BaseModelType:
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
        params (Optional[Dict[str, Optional[ParamTypes]]]): The params if any
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
        response = await HttpClient.make_post_request(url=url,data=json_body, params=filtered_params, auth=get_auth())
        data = handle_response_with_status(
            response=response,
            model=model,
            error_message=error_message
        )

    except api_exceptions as e:
        raise e
    except Exception as e:
        raise Exception(
            f"{error_message} Exception: {e}") from e

    return data
