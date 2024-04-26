from abc import ABC, abstractmethod

class AuthManager(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def refresh(self):
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
    def handle_auth_flow(self):
        """Handle any user interactions required for auth flow."""
        pass

    @abstractmethod
    def validate_token(self):
        """Validate the token checking expiry and credentials."""
        pass




