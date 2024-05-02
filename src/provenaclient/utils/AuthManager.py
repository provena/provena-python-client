from abc import ABC, abstractmethod

class AuthManager(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def perform_refresh(self):
        """ Refresh the current token"""
        pass

    @abstractmethod
    def perform_refresh_token(self):
        """ Refresh the current token"""
        pass

    @abstractmethod
    def force_refresh(self):
        """ Force refresh the current token"""
        pass

    @abstractmethod
    def get_token(self):
        """Get token information and other metadata."""
        pass

    @abstractmethod
    def get_auth(self):
        """Get the auth object."""
        pass

    @abstractmethod
    def validate_token(self):
        """Validate the token checking expiry and credentials."""
        pass




