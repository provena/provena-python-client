from typing import Optional

class AuthException(Exception): 
    def __init__(self, message: str, error_code: Optional[int] = None, payload: Optional[str] = None) -> None:

        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.payload = payload

    def __str__(self) -> str:

        base_message = self.message

        if self.error_code is not None: 
            base_message = base_message + f"Status code error: {self.error_code}"

        if self.payload is not None: 
            base_message = base_message + f"Server Details: {self.payload}"
        
        return base_message

    

class ValidationException(Exception):
    def __init__(self, message: str, error_code: Optional[int] = None, payload: Optional[str] = None) -> None:

        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.payload = payload

    def __str__(self) -> str:

        base_message = self.message

        if self.error_code is not None: 
            base_message = base_message + f"Status code error: {self.error_code}"

        if self.payload is not None: 
            base_message = base_message + f"Server Details: {self.payload}"
        
        return base_message


class ServerException(Exception):
    def __init__(self, message: str, error_code: Optional[int] = None, payload: Optional[str] = None) -> None:

        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.payload = payload

    def __str__(self) -> str:
                
        base_message = self.message

        if self.error_code is not None: 
            base_message = base_message + f"Status code error: {self.error_code}"

        if self.payload is not None: 
            base_message = base_message + f"Server Details: {self.payload}"
        
        return base_message



  



