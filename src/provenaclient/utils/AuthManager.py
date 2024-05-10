from abc import ABC, abstractmethod
from typing import Dict, Any
from .auth_helpers import BearerAuth, Tokens, HttpxBearerAuth

class AuthManager(ABC):

    @abstractmethod
    def perform_refresh(self) -> Dict[str, Any]:
        """ Refresh the current token"""
        pass

    @abstractmethod
    def perform_refresh_token(self) -> None:
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
        """Get the auth object."""
        pass

    @abstractmethod
    def get_async_auth(self) -> HttpxBearerAuth:
        """Get the httpx compatible auth object"""
        pass

    @abstractmethod
    def validate_token(self, tokens: Tokens) -> bool:
        """Validate the token checking expiry and credentials."""
        pass




