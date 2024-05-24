from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional, Tuple, TypeVar, Type
import json
from httpx import Response
from provenaclient.utils.exceptions import AuthException, HTTPValidationException, ServerException, BadRequestException, ValidationException
from ProvenaInterfaces.SharedTypes import StatusResponse


api_exceptions = (AuthException, HTTPValidationException, ValidationException, ServerException, BadRequestException)

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
def handle_model_parsing(response: Dict[str, Any], model: Type[T]) -> T:
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
    T
        Returns a python datatype that conforms to the structure
        of the provided model.
    """
    
    try: 
        parsed_model = model.parse_obj(response)
        return parsed_model

    except ValidationError as e:
        raise e
    

def parse_response_to_json(response: Response) -> Tuple[Dict[str, Any], StatusResponse]: 

    """Parses the httpx.response into a dictionary with proper error handling and
    also returns the parsed status object. 

    Returns
    -------
    Tuple[Dict[str, Any], StatusResponse]
        A tuple containing the parsed JSON response and a interactive python
        datatype parsed status through pydantic.

    Raises
    ------
    ValidationException
        An exception with a message that JSON parsing parsing failed of httpx.response
        object.
    ValidationException
        An exception with a message that pydantic parsing failed.
    """

    try: 
        parsed_response = response.json()

    except json.JSONDecodeError as e: 
        raise ValidationException("JSON parsing failed") from e

    try:
        parsed_status = StatusResponse.parse_obj(parsed_response)
    
    except ValidationError as e:
        raise ValidationException ("Pydantic parsing failed") from e

    return parsed_response, parsed_status    

def handle_response(response: Response, error_message: Optional[str]) -> None:
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

    if response.status_code == 400:
        raise BadRequestException(message = "Bad Request", error_code = 400, payload = error_message)

    if response.status_code == 401:
        raise AuthException(message = "Authentication failed", error_code = 401, payload = error_message)

    if response.status_code == 422:
        # This is a specific status code of this URL.
        raise HTTPValidationException(message =" Validation error", error_code = 422, payload = error_message)
    
    if response.status_code >=500:
        # Raise another exception here 
        raise ServerException(message = "Server error occurred", error_code = response.status_code, payload = error_message )

