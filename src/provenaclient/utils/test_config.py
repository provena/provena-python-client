from .Config import Config
from .Config import ToolingEnvironment, APIOverrides

config = Config(
    domain="dev.provena.rrap-is.com",
    realm_name="TODO"
)


auth_api_endpoint = config.auth_api_endpoint
print(config.prov_api_endpoint)
print(auth_api_endpoint)


# params = {"some_param": "some_value"}
# environment = config.get_environment("Production", params).prov_api_endpoint
# print(environment)


