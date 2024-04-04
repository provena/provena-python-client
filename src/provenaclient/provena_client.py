class Settings:
    def __init__(self, domain):
        self.domain = domain

class Auth:
    def __init__(self, settings):
        self.settings = settings

class Client:
    def __init__(self, auth, settings):
        self.auth = auth
        self.settings = settings

