from pydantic import BaseModel
from ProvenaInterfaces.RegistryModels import ItemDataset
from typing import List, Union

class SearchItem(BaseModel):
    id: str
    score: float
    
class LoadedSearchItem(SearchItem):
    item: ItemDataset
    
class UnauthorisedSearchItem(SearchItem):
    pass

class FailedSearchItem(SearchItem):
    error_info : str

class VersionDatasetRequest(BaseModel):
    id: str
    reason: str

class VersionDatasetResponse(BaseModel):
    new_version_id: str
    version_job_session_id: str

class RevertMetadata(BaseModel):
    id: str 
    history_id: int
    reason: str

class LoadedSearchResponse(BaseModel):
    # The successfully loaded search results
    items: List[LoadedSearchItem]
    auth_errors: List[UnauthorisedSearchItem]
    misc_errors: List[FailedSearchItem]