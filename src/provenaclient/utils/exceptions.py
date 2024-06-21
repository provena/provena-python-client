'''
Created Date: Thursday May 30th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday May 30th 2024 10:17:36 am +1000
Modified By: Peter Baker
-----
Description: Defines a collection of exceptions produced by the Provena Client, extending a common base handled exception.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from typing import Optional

import httpx


class BaseException(Exception):
    """A custom exception class that inherits from python's base exception.

    Parameters
    ----------
    Exception : Exception
        Exception class provided by python.
    """

    message: str
    error_code: Optional[int]
    payload: Optional[str]

    def __init__(self, message: str, error_code: Optional[int] = None, payload: Optional[str] = None) -> None:
        """Initialise the BaseException with a message, optional error code, and optional payload message from
        the API response. 

        Parameters
        ----------
        message : str
            The error message describing the exception
        error_code : Optional[int], optional
            The HTTP status code associated with the error, by default None
        payload : Optional[str], optional
            Additional information of the error received from API error response, by default None
        """

        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.payload = payload

    def __str__(self) -> str:
        """Creates a string of the BaseException

        Returns
        -------
        str
            A string describing the exception, including the message, error code, and payload if present.
        """

        base_message = f"Exception: {self.message}"

        if self.error_code is not None:
            base_message += f"\nStatus code error: {self.error_code}"

        if self.payload is not None:
            base_message += f"\nServer Details: {self.payload}"

        return base_message


class CustomTimeoutException(httpx.TimeoutException):
    """ An exception raised when a timeout occurs during an HTTP request.

    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """

    def __init__(self, message: str, url: Optional[str]) -> None:
        """Initialise the BaseException with a message and an optional URL.

        Parameters
        ----------
        message : str
            Message indicating HTTP timeout has occurred.
        url : Optional[str]
            URL related to timeout.
        """

        super().__init__(message)
        self.message = message
        self.url = url

    def __str__(self) -> str:
        """An exception raised when a timeout occurs during an HTTP request.


        Returns
        -------
        str
            Returns a string that includes both the error message and the URL related to the timeout, if provided.

        """

        base_message = self.message

        if self.url:
            base_message = base_message + self.url

        return base_message


class BadRequestException(BaseException):
    """An exception raised for HTTP 400 Bad Request errors.


    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """
    pass


class NotFoundException(BaseException):
    """An exception raised for HTTP 404 Not found exceptions.


    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """
    pass


class AuthException(BaseException):
    """An exception raised for HTTP 401 Unauthorized errors.

    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """
    pass


class HTTPValidationException(BaseException):
    """An exception raised for HTTP 422 Unprocessable Entity errors.


    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """
    pass


class ServerException(BaseException):
    """An exception raised for HTTP 500+ Server Error responses.


    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """
    pass


class ValidationException(BaseException):
    """An exception that is raised for validation/parsing
    errors that occurs through the client library.

    Parameters
    ----------
    BaseException
        A custom exception class that inherits from python's base exception
        and takes more parameters.
    """
