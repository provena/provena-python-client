from pydantic import BaseModel, ValidationError
from typing import BinaryIO, Dict, Any, List, Optional, Tuple, TypeVar, Type, Union, ByteString
import json
from httpx import Response
from provenaclient.utils.exceptions import AuthException, HTTPValidationException, ServerException, BadRequestException, ValidationException, NotFoundException
from provenaclient.utils.exceptions import BaseException
from ProvenaInterfaces.SharedTypes import StatusResponse
from ProvenaInterfaces.RegistryModels import ItemBase
import os

# Type var to refer to base models
BaseModelType = TypeVar("BaseModelType", bound=BaseModel)
ItemModelType = TypeVar("ItemModelType", bound=ItemBase)

# Type alias for json data
JsonData = List[Dict[str, Any]] | Dict[str, Any]
# Type alias for httpx file upload.
HttpxFileUpload = Dict[str, Tuple[str, ByteString, str]]

ParamTypes = Union[str, int, bool]


def write_file_helper(file_name: str, path_to_save_at: Optional[str], content: str) -> None:
    """
    Writes provided content to a file.

    Parameters
    ----------
    file_name : str
        The name of the file to write content into.
    content : str
        The content to be written into the file.

    Raises
    ------
    IOError
        If an I/O error occurs during file operations.
    Exception
        For non-I/O related exceptions that may occur during file writing.
    """

    try:
        if path_to_save_at:
            if not os.path.isdir(path_to_save_at):
                raise ValueError(f"The provided path {path_to_save_at} is incorrect. Please try again.")
            file_path = os.path.join(path_to_save_at, file_name)

        else:
            file_path = file_name

        # Write to file
        with open(file_path, 'w') as file:
            file.write(content)

    except IOError as e:
        raise IOError(f"Failed to file {file_name} due to I/O error: {e}")

    except Exception as e:
        raise Exception(f"File writing failed. Exception {e}")

    
def prepare_httpx_files_csv_request(file_path: str) -> HttpxFileUpload:

    # This method could be made more "generic" to accept various file types
    # however, I have scoped it to csv for our use cases.

    """Prepares an httpx files request object.

    Parameters
    ----------
    file_path : str
        The path of an existing created file.
    Returns
    -------
    HttpxFileUpload
        A dictionary representing file(s) to be uploaded with the
        request. Each key in the dictionary is the name of the form field for the file according,
        to API specifications. For Provena it's "csv_file" and and the value 
        is a tuple of (filename, filedata or file contents, MIME type or media type).

    Raises
    ------
    Exception
        If there any error with reading the CSV file 
        this general exception is raised.
    """

    try:
            file = open(file_path, 'rb')  # Open the file in binary-read mode
            file_content = file.read() # Save the contents of the file.
            files = {'csv_file': (file_path, file_content, 'text/csv')}  # Prepare the request object, passed to httpx.
            file.close()

            return files

    except Exception as e:
        raise Exception(f"Error with CSV file. Exception {e}")

def build_params_exclude_none(params: Dict[str, Optional[ParamTypes]]) -> Dict[str, ParamTypes]:
    """

    Takes a raw params dict with optional args and returns filtered.

    Args:
        params (Dict[str, Optional[ParamTypes]]): The input raw dict

    Returns:
        Dict[str, ParamTypes]: The filtered param list with no None values
    """
    return {id: val for id, val in params.items() if val is not None}


def py_to_dict(model: BaseModel) -> JsonData:
    """ This helper function converts a Pydantic model to a Python dictionary.

    Requires a pydantic dump into serialised JSON to be safe against all object
    types

    Parameters
    ----------
    model : BaseModel
        The instance of the model that needs to be converted to a dict. 

    Returns
    -------
    JsonData
        A python dictionary object which contains the fields and values of the
        base model that are not none.
    """

    return json.loads(model.json(exclude_none=True))


def handle_model_parsing(json_data: JsonData, model: Type[BaseModelType]) -> BaseModelType:
    """This generic helper function parses a HTTP Response into a
    python datatype based on a pydantic defined model.

    Parameters
    ----------
    json_data : JsonData
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
        parsed_model = model.parse_obj(json_data)
        return parsed_model
    except ValidationError as e:
        raise e


def parse_json_payload(response: Response) -> JsonData:
    """

    Parses a HTTPX response object into JSON handling the error if any occurs.

    Args:
        response (Response): The raw HTTP response.

    Raises:
        ValidationException: If JSON decoding fails, handles and raises error.

    Returns:
        JsonData: The returned dictionary object representing JSON data.
    """
    try:
        parsed_response = response.json()

    except json.JSONDecodeError as e:
        raise ValidationException("JSON parsing failed") from e

    return parsed_response


def handle_err_codes(response: Response, error_message: Optional[str]) -> None:
    """

    This helper function checks the status code of the HTTP response and raises
    a custom exception accordingly.

    Also embeds error info from JSON or text result.

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

    text: Union[str, None] = None
    try:
        data = response.json()
        text = json.dumps(data, indent=2)
    except Exception:
        text = response.text

    if response.status_code == 400:
        raise BadRequestException(
            message=f"Bad Request. Details: {text}.", error_code=400, payload=error_message)

    if response.status_code == 401:
        raise AuthException(message=f"Authentication failed. Details: {text}.",
                            error_code=401, payload=error_message)

    if response.status_code == 404:
        raise NotFoundException(message=f"Url was not found at provided service endpoint. Details: {text}.",
                                error_code=404, payload=error_message)

    if response.status_code == 422:
        # This is a specific status code of this URL.
        raise HTTPValidationException(
            message=f"Validation error. Details: {text}.", error_code=422, payload=error_message)

    if response.status_code != 200:
        # Raise another exception here
        raise ServerException(message=f"Server error occurred. Details: {text}.",
                              error_code=response.status_code, payload=error_message)


def check_status_response(json_data: JsonData) -> None:
    """
    Parses JSON data as StatusResponse model, then asserts success is true,
    throwing exception with embedded details if not.

    Args:
        json_data (Dict): The JSON data to parse

    Raises:
        Exception: Exception if status if False
    """
    # Check model parses
    status_obj = handle_model_parsing(
        json_data=json_data, model=StatusResponse)

    # Check status is success
    if not status_obj.status.success:
        raise Exception(
            f"Status object from API indicated failure. Details: {status_obj.status.details}.")


def check_codes_and_parse_json(response: Response, error_message: Optional[str]) -> JsonData:
    """

    Given raw response, validates codes and parses as JSON.

    Args:
        response (Response): The raw http client response
        error_message (Optional[str]): The error message to embed if any

    Returns:
        JsonData: The json data post parse
    """
    # Check codes
    handle_err_codes(response=response, error_message=error_message)

    # Handle JSON parsing
    json_data = parse_json_payload(response=response)

    return json_data


def handle_response_non_status(response: Response, model: Type[BaseModelType], error_message: Optional[str]) -> BaseModelType:
    """
    Given the raw response from http client, and the model, will validate

    - 200 OK code (with common errors handled)
    - Parsed as JSON
    - Parsed as desired final model

    Returns the parsed pydantic object.

    Args:
        response (Response): The raw response from http client
        model (Type[T]): The model type (not instance) to parse against
        error_message (Optional[str]): The error message to embed into exceptions.

    Returns:
        T: The parsed model
    """

    # Handle JSON parsing and codes
    json_data = check_codes_and_parse_json(
        response=response, error_message=error_message)

    # Check model parses
    parsed_obj = handle_model_parsing(json_data=json_data, model=model)

    return parsed_obj



def handle_response_with_status(response: Response, model: Type[BaseModelType], error_message: Optional[str]) -> BaseModelType:
    """
    Given the raw response from http client, and the model, will validate

    - 200 OK code (with common errors handled)
    - Parsed as JSON
    - Parsed as StatusResponse and asserted for success=true, throwing with details if not
    - Parsed as desired final model

    Returns the parsed pydantic object.

    Args:
        response (Response): The raw response from http client
        model (Type[T]): The model type (not instance) to parse against
        error_message (Optional[str]): The error message to embed into exceptions.

    Returns:
        T: The parsed model
    """
    # Handle JSON parsing and codes
    json_data = check_codes_and_parse_json(
        response=response, error_message=error_message)

    # Check status result
    check_status_response(json_data=json_data)

    # Check model parses
    parsed_obj = handle_model_parsing(json_data=json_data, model=model)

    return parsed_obj
