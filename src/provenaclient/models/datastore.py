from pydantic import BaseModel
from ProvenaInterfaces.RegistryModels import ItemDataset
from typing import List

class SearchItem(BaseModel):
    id: str
    strength: float
    
class LoadedSearchItem(SearchItem):
    item: ItemDataset
    
class UnauthorisedSearchItem(SearchItem):
    pass

class FailedSearchItem(SearchItem):
    error_info : str
    
class LoadedSearchResponse(BaseModel):
    # The successfully loaded search results
    items: List[LoadedSearchItem]
    auth_errors: List[UnauthorisedSearchItem]
    misc_errors: List[FailedSearchItem]