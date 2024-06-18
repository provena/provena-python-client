'''
Created Date: Tuesday May 28th 2024 +1000
Author: Peter Baker
-----
Last Modified: Tuesday May 28th 2024 11:18:32 am +1000
Modified By: Peter Baker
-----
Description: Defines the primary config object for the Provena Client - notably the endpoints.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from pydantic import BaseModel
from typing import Optional

def optional_override_prefixor(domain: str, prefix: str, override: Optional[str]) -> str:
    """

    Helper function which performs the API prefixing while being override aware. 

    If override supplied - uses it directly. 

    If not, prefixes with protocol and prefix suitably.

    Args:
        domain (str): The domain base
        prefix (str): The API prefix
        override (Optional[str]): The optional override

    Returns:
        str: The URL
    """
    if override is not None:
        return override
    else:
        if prefix != "":
            return f"https://{prefix}.{domain}"
        else:
            return f"https://{domain}"


class APIOverrides(BaseModel):
    datastore_api_endpoint_override: Optional[str] = None
    auth_api_endpoint_override: Optional[str] = None
    registry_api_endpoint_override: Optional[str] = None
    prov_api_endpoint_override: Optional[str] = None
    search_api_endpoint_override: Optional[str] = None
    search_service_endpoint_override: Optional[str] = None
    handle_service_api_endpoint_override: Optional[str] = None
    jobs_service_api_endpoint_override: Optional[str] = None
    keycloak_endpoint_override: Optional[str] = None

class EndpointConfig(BaseModel):
    domain: str
    # What is the auth realm name?
    realm_name: str
    api_overrides: APIOverrides

class Config():

    def __init__(self, domain: str, realm_name: str, api_overrides: APIOverrides = APIOverrides()) -> None:
        """Creates a EndpointConfig object that holds relevant Provena instance information
        and possible overrides if provided.

        Parameters
        ----------
        domain : str
            The current domain that the Provena instance is deployed in.
        realm_name : str
            Your keycloak realm name.
        api_overrides : APIOverrides, optional
            Provide any overrides to certain API endpoints if you wish, by default APIOverrides() with all overrides set to None.
        """

        # the unpopulated environment
        self._api_config: EndpointConfig = EndpointConfig(domain=domain, realm_name=realm_name, api_overrides=api_overrides)
    
    # Property methods to retrieve different API endpoints. 

    @property
    def search_api_endpoint(self) -> str:
        """Generate the search api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the search api endpoint.
        """
        
        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="search",
            override= self._api_config.api_overrides.search_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def jobs_service_api_endpoint(self) -> str:
        """Generate the job api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the job api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="job-api",
            override=self._api_config.api_overrides.jobs_service_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def handle_service_api_endpoint(self) -> str:
        """Generate the handle_service api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the handle_service api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="handle",
            override=self._api_config.api_overrides.handle_service_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def search_service_endpoint(self) -> str:
        """Generate the search_service api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the search_service api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="search-service",
            override=self._api_config.api_overrides.search_service_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def auth_api_endpoint(self) -> str:
        """Generate the auth api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the auth api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="auth-api",
            override=self._api_config.api_overrides.auth_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def prov_api_endpoint(self) -> str:
        """Generate the prov api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the prov api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="prov-api",
            override=self._api_config.api_overrides.prov_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def datastore_api_endpoint(self) -> str:
        """Generate the datastore api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the datastore api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="data-api",
            override=self._api_config.api_overrides.datastore_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def registry_api_endpoint(self) -> str:
        """Generate the registry api endpoint based on the 
        provided domain, prefix and possible override value. 

        Returns
        -------
        str
            A string containing the registry api endpoint.
        """

        return optional_override_prefixor(
            domain=self._api_config.domain,
            prefix="registry-api",
            override=self._api_config.api_overrides.registry_api_endpoint_override if self._api_config.api_overrides else None
        )

    @property
    def keycloak_endpoint(self) -> str:
        """Generate the keycloak realm endpoint using domain, realm_name and possible 
        override value. 

        Returns
        -------
        str
            A string containing the keycloak realm endpoint.
        """

        endpoint = ""
        if self._api_config.api_overrides.keycloak_endpoint_override is not None:
            endpoint = self._api_config.api_overrides.keycloak_endpoint_override
        else:
            endpoint = f"https://auth.{self._api_config.domain}/auth/realms/{self._api_config.realm_name}"
        return endpoint
    

    
    
