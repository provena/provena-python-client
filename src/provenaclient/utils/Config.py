from pydantic import BaseModel

from typing import List, Dict, Any, Optional


''''
 1. There is an existing Tooling Environment class that allows us to hold different/numerous environments of Provena and it's information. 

 2. Our goal is to create a config class, that the user will insinitate, and in that pass in the values of name, domain and realm name. 

 3. The user will not declare or insintate the Tooling Envrionment class either, we will have to manage that internally. 

'''


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

class ToolingEnvironment(BaseModel):
    domain: str
    # What is the auth realm name?
    realm_name: str
    api_overrides: APIOverrides

    # Defaults - overridable
    aws_region: str = "ap-southeast-2"

      # Auto derived properties (using parameters)
    @property
    def search_api_endpoint(self) -> str:
        
        return optional_override_prefixor(
            domain=self.domain,
            prefix="search",
            override=self.api_overrides.search_api_endpoint_override
        )

    @property
    def jobs_service_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="job-api",
            override=self.api_overrides.jobs_service_api_endpoint_override
        )

    @property
    def handle_service_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="handle",
            override=self.api_overrides.handle_service_api_endpoint_override
        )

    @property
    def search_service_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="search-service",
            override=self.api_overrides.search_service_endpoint_override
        )

    @property
    def auth_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="auth-api",
            override=self.api_overrides.auth_api_endpoint_override
        )

    @property
    def prov_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="prov-api",
            override=self.api_overrides.prov_api_endpoint_override
        )

    @property
    def datastore_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="data-api",
            override=self.api_overrides.datastore_api_endpoint_override
        )

    @property
    def registry_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="registry-api",
            override=self.api_overrides.registry_api_endpoint_override
        )

    @property
    def keycloak_endpoint(self) -> str:
        endpoint = ""
        if self.api_overrides.keycloak_endpoint_override is not None:
            endpoint = self.api_overrides.keycloak_endpoint_override
        else:
            endpoint = f"https://auth.{self.domain}/auth/realms/{self.realm_name}"
        return endpoint

'''
class PopulatedToolingEnvironment(ToolingEnvironment):
    # This is the populated set of CLI parameters
    # parameters: ReplacementDict

    # def validate_parameters(self) -> None:
    #     """

    #     Validates the replacements vs parameters. 

    #     Raises:
    #         ValueError: Parameters missing/undefined
    #         ValueError: Missing particular parameter id
    #     """
    #     if len(self.replacements) > 0:
    #         if self.parameters is None:
    #             raise ValueError(
    #                 "No replacements provided for an environment which requires parameters.")

    #         # have some replacements ready
    #         required = set([r.id for r in self.replacements])
    #         provided = set(self.parameters.keys())

    #         missing = required - provided

    #         if len(missing) > 0:
    #             raise ValueError(
    #                 f"Insufficient number of parameter replacements for ToolingEnvironment. Expected {len(required)} got {len(missing)}. Missing the following: {missing}.")



    # Auto derived properties (using parameters)
    @property
    def search_api_endpoint(self) -> str:
        
        return optional_override_prefixor(
            domain=self.domain,
            prefix="search",
            override=self.api_overrides.search_api_endpoint_override
        )

    @property
    def jobs_service_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="job-api",
            override=self.api_overrides.jobs_service_api_endpoint_override
        )

    @property
    def handle_service_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="handle",
            override=self.api_overrides.handle_service_api_endpoint_override
        )

    @property
    def search_service_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="search-service",
            override=self.api_overrides.search_service_endpoint_override
        )

    @property
    def auth_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="auth-api",
            override=self.api_overrides.auth_api_endpoint_override
        )

    @property
    def prov_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="prov-api",
            override=self.api_overrides.prov_api_endpoint_override
        )

    @property
    def datastore_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="data-api",
            override=self.api_overrides.datastore_api_endpoint_override
        )

    @property
    def registry_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self.domain,
            prefix="registry-api",
            override=self.api_overrides.registry_api_endpoint_override
        )

    @property
    def keycloak_endpoint(self) -> str:
        endpoint = ""
        if self.api_overrides.keycloak_endpoint_override is not None:
            endpoint = self.api_overrides.keycloak_endpoint_override
        else:
            endpoint = f"https://auth.{self.domain}/auth/realms/{self.realm_name}"
        return endpoint

    # def get_endpoint_map(self) -> Dict[str, str]:
    #     # Helper function for the integration test wrapper
    #     return {
    #         "DATA_STORE_API_ENDPOINT": self.datastore_api_endpoint,
    #         "REGISTRY_API_ENDPOINT": self.registry_api_endpoint,
    #         "PROV_API_ENDPOINT": self.prov_api_endpoint,
    #         "AUTH_API_ENDPOINT": self.auth_api_endpoint
    #     }

     Use cases to think about: 

     1. Is it better to declare the ToolingEnvironment class outside the config, and pass into config instead? So user can 
     see all the type hints and maybe easier for testing?

     2. Can the populated tooling manager property methods be taken and be integrated elsewhere?? 

     1. Should the user be allowed to have multiple environments?
     2. If yes then the current approach of accessing is fine I think.

     1. If the user should not be allowed to have multiple environments, then the current approach needs to be tweaked. 

    '''

class Config():

    def __init__(self, domain: str, realm_name: str, api_overrides: Optional[APIOverrides] = APIOverrides()):
        
        # the unpopulated environment
        self._environment: ToolingEnvironment = ToolingEnvironment(domain=domain, realm_name=realm_name, api_overrides=api_overrides)

    
    #uncomment.

    def get_environment(self) -> ToolingEnvironment: # type: ignore
        """
        Fetches the environment based on the ToolingEnvironment name and the set
        of parameter replacements.

        Args:
            name (str): The tooling environment "name" field
            params (ReplacementDict): The replacement dictionary - use
            process_params to generate this from CLI args

        Raises:
            ValueError: Throws an error if environment doesn't exist

        Returns:
            PopulatedToolingEnvironment: A populated and validated version of
            the environment ready to use.
        """        
        unpopulated = self._environment
        if unpopulated is None:
            raise ValueError(
                f"Unpopulated environment does not exist.")
        populated = ToolingEnvironment(**unpopulated.dict())
        # populated.validate_parameters()
        return populated
    
    # Alternative to using the get_environment method. 

    @property
    def search_api_endpoint(self) -> str:
        
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="search",
            override= self._environment.api_overrides.search_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def jobs_service_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="job-api",
            override=self._environment.api_overrides.jobs_service_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def handle_service_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="handle",
            override=self._environment.api_overrides.handle_service_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def search_service_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="search-service",
            override=self._environment.api_overrides.search_service_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def auth_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="auth-api",
            override=self._environment.api_overrides.auth_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def prov_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="prov-api",
            override=self._environment.api_overrides.prov_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def datastore_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="data-api",
            override=self._environment.api_overrides.datastore_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def registry_api_endpoint(self) -> str:
        return optional_override_prefixor(
            domain=self._environment.domain,
            prefix="registry-api",
            override=self._environment.api_overrides.registry_api_endpoint_override if self._environment.api_overrides else None
        )

    @property
    def keycloak_endpoint(self) -> str:
        endpoint = ""
        if self._environment.api_overrides.keycloak_endpoint_override is not None:
            endpoint = self._environment.api_overrides.keycloak_endpoint_override
        else:
            endpoint = f"https://auth.{self._environment.domain}/auth/realms/{self._environment.realm_name}"
        return endpoint
    

    
    
