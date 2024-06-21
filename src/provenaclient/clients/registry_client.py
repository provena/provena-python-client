'''
Created Date: Thursday June 6th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday June 6th 2024 1:39:55 pm +1000
Modified By: Peter Baker
-----
Description: Incomplete Registry API L2 Client.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

18-06-2024 | Peter Baker | Initial structure setup to help dispatch into the various sub types in the L3.
'''

from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from provenaclient.utils.registry_endpoints import *
from ProvenaInterfaces.RegistryModels import *


class GenericRegistryEndpoints(str, Enum):
    GET_HEALTH_CHECK = "/"
    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"
    GET_REGISTRY_GENERAL_ABOUT_VERSION = "/registry/general/about/version"
    GET_REGISTRY_GENERAL_FETCH = "/registry/general/fetch"
    POST_REGISTRY_GENERAL_LIST = "/registry/general/list"


class RegistryAdminEndpoints(str, Enum):
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_EXPORT = "/admin/export"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    POST_ADMIN_IMPORT = "/admin/import"
    POST_ADMIN_RESTORE_FROM_TABLE = "/admin/restore_from_table"


class RegistryAdminClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the RegistryClient with authentication and configuration.

        Parameters
        ----------
        auth: AuthManager
            An abstract interface containing the user's requested auth flow method.
        config: Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

    def _build_endpoint(self, endpoint: RegistryAdminEndpoints) -> str:
        return f"{self._config.registry_api_endpoint}{endpoint.value}"


# L2 interface.
class RegistryClient(ClientService):
    # Sub clients
    admin: RegistryAdminClient

    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the RegistryClient with authentication and configuration.

        Parameters
        ----------
        auth: AuthManager
            An abstract interface containing the user's requested auth flow method.
        config: Config
            A config object which contains information related to the Provena instance.
        """
        self._auth = auth
        self._config = config

        # Sub clients
        self.admin = RegistryAdminClient(auth=auth, config=config)

    # Function to get the endpoint URL
    def _build_subtype_endpoint(self, action: RegistryAction, item_subtype: ItemSubType) -> str:
        return subtype_action_to_endpoint(
            base=self._config.registry_api_endpoint,
            action=action,
            item_subtype=item_subtype
        )

    def _build_general_endpoint(self, endpoint: GenericRegistryEndpoints) -> str:
        return f"{self._config.registry_api_endpoint}{endpoint.value}"

    async def fetch_item(self, id: str, item_subtype: ItemSubType, fetch_response_model: Type[BaseModelType], seed_allowed: Optional[bool] = None) -> BaseModelType:
        """
        Ascertains the correct endpoint based on the subtype provided, then runs the fetch operation, parsing the data as the specified model.

        Args:
            id (str): The id of the item to fetch.
            item_subtype (ItemSubType): The subtype of the item to fetch.
            fetch_response_model (Type[BaseModelType]): The response pydantic model to parse as e.g. OrganisationFetchResponse
            seed_allowed (Optional[bool], optional): Should the endpoint throw an error if the item is a seed item?  Defaults to None.

        Returns:
            BaseModelType: _description_
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.FETCH, item_subtype=item_subtype)

        # fetch the item from the subtype specific endpoint
        return await parsed_get_request_with_status(
            client=self,
            params={'id': id, 'seed_allowed': seed_allowed},
            error_message=f"Failed to fetch item with id {id} and subtype {item_subtype}.",
            model=fetch_response_model,
            url=endpoint,
        )

    async def update_item(self, id: str, reason: Optional[str], item_subtype: ItemSubType, domain_info: DomainInfoBase, update_response_model: Type[BaseModelType]) -> BaseModelType:
        """
        Ascertains the correct endpoint then runs the update operation on an existing item by providing new domain info.

        Args:
            id (str): The id of item to update.
            reason (Optional[str]): The reason for updating, if any
            item_subtype (ItemSubType): The subtype to update
            domain_info (DomainInfoBase): The domain info to replace existing item with
            update_response_model (Type[BaseModelType]): The response model to parse e.g. StatusResponse

        Returns:
            BaseModelType: The response model parsed
        """
        # determine endpoint
        endpoint = self._build_subtype_endpoint(
            action=RegistryAction.UPDATE, item_subtype=item_subtype)

        # fetch the item from the subtype specific endpoint
        return await parsed_put_request_with_status(
            client=self,
            params={'id': id, 'reason': reason},
            json_body=py_to_dict(domain_info),
            error_message=f"Failed to update item with id {id} and subtype {item_subtype}.",
            model=update_response_model,
            url=endpoint,
        )
