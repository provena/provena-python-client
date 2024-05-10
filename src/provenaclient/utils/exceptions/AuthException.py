from typing import Optional

class AuthException(Exception): 
    def __init__(self, message: str, error_code: Optional[int] = None, payload: Optional[str] = None) -> None:

        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.payload = payload

    def __str__(self) -> str:

        # Create an error message here. 

        base_message = f"Auth Exception"


        return base_message