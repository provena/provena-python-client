from enum import Enum
from typing import Dict
 
# Define the Action Enum
class Action(str, Enum):
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
 
# Define the ItemSubType Enum
class ItemSubType(str, Enum):
    MODEL_RUN = "MODEL_RUN"
    ORGANISATION = "ORGANISATION"
    PERSON = "PERSON"
    MODEL = "MODEL"
    MODEL_RUN_WORKFLOW_TEMPLATE = "MODEL_RUN_WORKFLOW_TEMPLATE"
    DATASET_TEMPLATE = "DATASET_TEMPLATE"
    DATASET = "DATASET"
    CREATE = "CREATE"
    VERSION = "VERSION"
    STUDY = "STUDY"
 
# Define the mappings
action_postfixes: Dict[Action, str] = {
    Action.FETCH: "/fetch",
    Action.UPDATE: "/update",
    Action.REVERT: "/revert",
    Action.CREATE: "/create",
    Action.LIST: "/list",
    Action.SEED: "/seed",
    Action.VERSION: "/version",
    Action.SCHEMA: "/schema",
    Action.UI_SCHEMA: "/ui_schema",
    Action.VALIDATE: "/validate",
    Action.AUTH_EVALUATE: "/auth/evaluate",
    Action.AUTH_CONFIGURATION: "/auth/configuration",
    Action.AUTH_ROLES: "/auth/roles",
    Action.LOCK: "/locks/lock",
    Action.UNLOCK: "/locks/unlock",
    Action.LOCK_HISTORY: "/locks/history",
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