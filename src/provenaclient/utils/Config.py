from pydantic import BaseModel

class Config(BaseModel):
    
    # This will contain information about your Provena domain.
    registry_api_endpoint: str
    datastore_api_endpoint: str
