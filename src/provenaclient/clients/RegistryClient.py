#TODO


'''
from ..utils.Auth import Auth
from ..utils.Config import Config
from ..utils.httpClient import HttpClient
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.RegistryModel import *

class RegistryClient: 

    URL_MAP = {
        (REGISTRY_ACTION, SUBTYPE) : "url"
    }

    auth: Auth
    config: Config

    def __init__(self, auth: Auth, config: Config):
        self.auth = auth, 
        self.config = config

    async def fetch_item(request_model: RequestModel, entity_subtype: ItemSubType) -> ItemPerson: 

        # To complete this method. 
        get_auth = ()..

        try:
           url =self.URL_MAP[REGISTRY_API.FETCH_ITEM, entity_subtype]
        
        
        try:
            
            response = await HttpClient.make_get_request(url = url, body=request_model.dict(), params = validated_id.id, headers = get_auth_headers) # Retrieve the response object.
            
            # Handling the HTTP/Application level errors here
            if response.status_code != 200:
                if response.status_code == 401:
                    # TODO Define custom exceptions for common scenarios e.g. Auth
                    raise Exception(f"Authorisation exception...")
                if response.status_code >= 500:
                    raise UnexpectedException(...)
                    
        except Exception as e: 
            raise ValueError("Failed to fetch item.")
            
        # parse as json 
        json_response = response.json() 
        
        try:
            parsed_model = ItemModel.parse_json(json_response)
        except:
            # raise exception here for validation
        
        # check for status if applicable
        if not parsed_model.status:
            raise Exception(#status details
            )

'''