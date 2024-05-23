from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional, TypeVar
import json
from httpx import Response
from provenaclient.utils.exceptions import AuthException, ValidationException, ServerException, BadRequestException


def py_to_dict(model: BaseModel) -> Dict[str, Any]:
    """ This helper function converts a Pydantic model to a Python dictionary.

    Parameters
    ----------
    model : BaseModel
        The instance of the model that needs to be converted 
        to a dict. 

    Returns
    -------
    Dict[str, Any]
        A python dictionary object which contains the fields and values 
        of the base model that are not none.
    """

    return json.loads(model.json(exclude_none=True))


T = TypeVar("T", bound=BaseModel)    
def handle_model_parsing(response: Response, model: type[T]) -> Optional[T]:
    """This generic helper function parses a HTTP Response into a
    python datatype based on a pydantic defined model.

    Parameters
    ----------
    response : Response
        The response received after HTTP request. 
    model : type[T]
        The type of the model being casted from HTTP response 
        into python datatype. For example:
        MintResponse, RegistryFetchResponse.

    Returns
    -------
    Optional[T]
        Returns either a python datatype or None.
    """
    
    try: 
        json_response = response.json()
        parsed_model = model.parse_obj(json_response)
        return parsed_model

    except ValidationError as e:
        print("Failed to fetch this item.") 
        return None
    

def handle_response(response: Response) -> None:
    """This helper function checks the status code of 
    the HTTP response and raises a custom exception accordingly.

    Parameters
    ----------
    response : Response
        The httpx.response object.

    Raises
    ------
    BadRequestException
        Raised when the server returns a 400 status code.
    AuthException
        Raised when the server returns a 401 status code.
    ValidationException
        Raised when the server returns a 422 status code.
    ServerException
        Raised when the server returns a status code of 500 or above.
    """

    error_message = response.json().get('details')

    if response.status_code == 400:
        raise BadRequestException(message = "Bad Request", error_code = 400, payload = error_message)

    if response.status_code == 401:
        raise AuthException(message = "Authentication failed", error_code = 401, payload = error_message)

    if response.status_code == 422:
        # This is a specific status code of this URL.
        raise ValidationException(message =" Validation error", error_code = 422, payload = error_message)
    
    if response.status_code >=500:
        # Raise another exception here 
        raise ServerException(message = "Server error occurred", error_code = response.status_code, payload = error_message )

