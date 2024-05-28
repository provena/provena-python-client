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
