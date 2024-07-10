'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 5:00:47 pm +1000
Modified By: Peter Baker
-----
Description: General helper functions which are useful across the client library.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from pydantic import BaseModel, ValidationError
from typing import Dict, Any, List, Mapping, Optional, Tuple, TypeVar, Type, Union, ByteString
import json
from httpx import Response
from provenaclient.utils.exceptions import AuthException, HTTPValidationException, ServerException, BadRequestException, ValidationException, NotFoundException
from provenaclient.utils.exceptions import BaseException
from ProvenaInterfaces.SharedTypes import StatusResponse
from ProvenaInterfaces.RegistryModels import ItemBase, ItemSubType
import os

# Type var to refer to base models
BaseModelType = TypeVar("BaseModelType", bound=BaseModel)
ItemModelType = TypeVar("ItemModelType", bound=ItemBase)

# Type alias for json data
JsonData = Union[List[Dict[str, Any]],Dict[str, Any]]
# Type alias for httpx file upload.
HttpxFileUpload = Dict[str, Tuple[str, ByteString, str]]

ParamTypes = Union[str, int, bool]


def convert_to_item_subtype(item_subtype_str: Optional[str]) -> ItemSubType:
    """Converts a string into ItemSubType supported enum type.

    Parameters
    ----------
    item_subtype_str : Optional[str]
        Optional string containing similar enum text.

    Returns
    -------
    ItemSubType
        Enum type of ItemSubType.

    Raises
    ------
    ValueError
        Item subtype field was not present.
    ValueError
        Item subtype cannot be converted to ENUM.
    """

    if item_subtype_str is None:
        raise ValueError("Item subtype field not found!")
    
    try:
        return ItemSubType[item_subtype_str.upper()]
    except KeyError as e:
        raise ValueError(f"Invalid item_subtype: {item_subtype_str}") from e

def get_and_validate_file_path(file_path: Optional[str], write_to_file: bool, default_file_name: str) -> Optional[str]:
    """Determine and validate the file path for writing a file.

    If file_path is not provided and write_to_file is True then will use a dynamic 
    default file name. 

    Parameters
    ----------
    file_path : Optional[str]
        The path to save the file at.
    write_to_file : bool
        A boolean flag  indicating whether writing to the file is enabled.
    default_file_name : str
        The default file name to use if file_path is not provided.

    Returns
    -------
    Optional[str]
        The validated file path, or None if writing to file is not enabled.

    Raises
    ------
    ValueError
        If a file path is provided but writing to the file is not enabled.
    """

    if file_path and not write_to_file:
        raise ValueError(f"Write to CSV must be enabled. Currently {write_to_file}")
    
    if file_path and write_to_file:
        # Validate provided file path directory.
        validate_existing_path(file_path)

    if not file_path and write_to_file:
        # Create default file path directory.
        file_path = default_file_name

    return file_path

def validate_existing_path(file_path: str) -> None :
    """Validates a provided file path, and checks if 
    the directory exists. 

    Parameters
    ----------
    file_path : str
        The file path to validate.

    Raises
    ------
    ValueError
        If the directory part of the path does not exist.
    IOError
        If an I/O error occurs during file operations.
    Exception
        For any other exceptions that may occur.
    """

    try:
        # Validates if the provided directory part of the file path exists.
        directory = os.path.dirname(file_path)
        if not os.path.isdir(directory):
            raise ValueError(f"The provided path {file_path} is incorrect. Please try again.")
        
    except IOError as e:
        raise IOError(f"Failed to validate {file_path} due to I/O error: {e}")

    except Exception as e:
        raise Exception(f"Path validation failed. Exception {e}")


def write_file_helper(file_path: str, content: str) -> None:
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
        # Write to file
        with open(file_path, 'w') as file:
            file.write(content)

    except IOError as e:
        raise IOError(f"Failed to file {file_path} due to I/O error: {e}")

    except Exception as e:
        raise Exception(f"File writing failed. Exception {e}")

    
def read_file_helper(file_path: str) -> str:

    """Reads a valid file and returns its content

    Parameters
    ----------
    file_path : str
        The path of an existing created file.
    Returns
    -------
    str
        A string representation of the file contents.

    Raises
    ------
    Exception
        If there any error with reading the file 
        this general exception is raised.
    """

    try:
            file = open(file_path, 'r')  # Open the file in read mode
            file_content = file.read() # Save the contents of the file.
            file.close()

            return file_content

    except Exception as e:
        raise Exception(f"Error with file. Exception {e}")

def build_params_exclude_none(params: Mapping[str, Optional[ParamTypes]]) -> Dict[str, ParamTypes]:
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
