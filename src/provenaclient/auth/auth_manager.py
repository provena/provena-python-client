from abc import ABC, abstractmethod
from typing import Dict, Any
from .auth_helpers import BearerAuth, Tokens

class AuthManager(ABC):

    @abstractmethod
    def make_token_refresh_request(self) -> Dict[str, Any]:
        """ Refresh the current token"""
        pass

    @abstractmethod
    def refresh_tokens(self) -> None:
        """ Refresh the current token"""
        pass

    @abstractmethod
    def force_refresh(self) -> None:
        """ Force refresh the current token"""
        pass

    @abstractmethod
    def get_token(self) -> str:
        """Get token information and other metadata."""
        pass

    @abstractmethod
    def get_auth(self) -> BearerAuth:
        """Prepares and returns an auth object of Bearer type."""
        pass

    @abstractmethod
    def validate_token(self, tokens: Tokens) -> bool:
        """Validate the token by checking its expiry and signatures."""
        pass




