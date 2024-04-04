from provenaclient.provena_client import Auth, Client, Settings 

settings = Settings(
    domain = "mds.gbrrestoration.org"
)

auth = Auth(
    settings = settings
)

client = Client(
    auth = auth, 
    settings = settings
)