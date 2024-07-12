'''
Created Date: Thursday June 6th 2024 +1000
Author: Peter Baker
-----
Last Modified: Thursday June 6th 2024 1:39:55 pm +1000
Modified By: Peter Baker
-----
Description: Set of route maps for the Registry API used to help generate routes from subtype + Action combinations.
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from enum import Enum
from typing import Dict
from ProvenaInterfaces.RegistryModels import ItemSubType
 
class RegistryAction(str, Enum):
    FETCH = "FETCH"
    UPDATE = "UPDATE"
    CREATE = "CREATE"
    LIST = "LIST"
    SEED = "SEED"
    VERSION = "VERSION"
    SCHEMA = "SCHEMA"
    UI_SCHEMA = "UI_SCHEMA"
    VALIDATE = "VALIDATE"
    AUTH_EVALUATE = "AUTH_EVALUATE"
    AUTH_CONFIGURATION = "AUTH_CONFIGURATION"
    AUTH_ROLES = "AUTH_ROLES"
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    REVERT = "REVERT"
    LOCK_HISTORY = "LOCK_HISTORY"
    DELETE = "DELETE"
 
# Define the mappings
action_postfixes: Dict[RegistryAction, str] = {
    RegistryAction.FETCH: "/fetch",
    RegistryAction.UPDATE: "/update",
    RegistryAction.REVERT: "/revert",
    RegistryAction.CREATE: "/create",
    RegistryAction.LIST: "/list",
    RegistryAction.SEED: "/seed",
    RegistryAction.VERSION: "/version",
    RegistryAction.SCHEMA: "/schema",
    RegistryAction.UI_SCHEMA: "/ui_schema",
    RegistryAction.VALIDATE: "/validate",
    RegistryAction.AUTH_EVALUATE: "/auth/evaluate",
    RegistryAction.AUTH_CONFIGURATION: "/auth/configuration",
    RegistryAction.AUTH_ROLES: "/auth/roles",
    RegistryAction.LOCK: "/locks/lock",
    RegistryAction.UNLOCK: "/locks/unlock",
    RegistryAction.LOCK_HISTORY: "/locks/history",
    RegistryAction.DELETE: "/delete"
}
 
subtype_route_prefixes: Dict[ItemSubType, str] = {
    ItemSubType.MODEL_RUN: "/registry/activity/model_run",
    ItemSubType.ORGANISATION: "/registry/agent/organisation",
    ItemSubType.PERSON: "/registry/agent/person",
    ItemSubType.MODEL: "/registry/entity/model",
    ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE: "/registry/entity/model_run_workflow",
    ItemSubType.DATASET_TEMPLATE: "/registry/entity/dataset_template",
    ItemSubType.DATASET: "/registry/entity/dataset",
    ItemSubType.CREATE: "/registry/activity/create",
    ItemSubType.VERSION: "/registry/activity/version",
    ItemSubType.STUDY: "/registry/activity/study",
}
 
# Function to get the endpoint URL
def subtype_action_to_endpoint(base: str, action: RegistryAction, item_subtype: ItemSubType) -> str:
    """
    
    Generates a fully formed registry URL given the below params

    Args:
        base (str): The URL base e.g. https://registry.provena.com
        action (RegistryAction): The action to be taken, see enum
        item_subtype (ItemSubType): The subtype to get the route for

    Returns:
        str: The fully formed URL
    """
    subtype_prefix = subtype_route_prefixes[item_subtype]
    action_postfix = action_postfixes[action]
    return f"{base}{subtype_prefix}{action_postfix}"