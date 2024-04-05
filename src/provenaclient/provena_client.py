from dataclasses import dataclass

@dataclass
class Settings:
    domain: str
    
class Auth:
    def __init__(self, settings: Settings):
        self.settings = settings

class Client:
    def __init__(self, auth: Auth, settings: Settings):
        self.auth = auth
        self.settings = settings

