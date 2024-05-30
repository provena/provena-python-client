from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.utils.http_client import HttpClient
from enum import Enum
from provenaclient.utils.helpers import *
from provenaclient.clients.client_helpers import *
from provenaclient.models.registry import * 


"""

  Commenting out the below ENUM's for now, will remove once we are set on using the URL_MAP approach above.

class RegistryAccessEndpoints(str, Enum):
    ENUM containing endpoints for check-access.

    GET_CHECK_ACCESS_CHECK_ADMIN_ACCESS = "/check-access/check-admin-access"
    GET_CHECK_ACCESS_CHECK_GENERAL_ACCESS = "/check-access/check-general-access"
    GET_CHECK_ACCESS_CHECK_READ_ACCESS = "/check-access/check-read-access"
    GET_CHECK_ACCESS_CHECK_WRITE_ACCESS = "/check-access/check-write-access"

class RegistryEndpoints(str, Enum):
    ENUM containing endpoints for registry.

    GET_HEALTH_CHECK = "/"

    GET_REGISTRY_ACTIVITY_CREATE_AUTH_CONFIGURATION = "/registry/activity/create/auth/configuration"
    GET_REGISTRY_ACTIVITY_CREATE_AUTH_EVALUATE = "/registry/activity/create/auth/evaluate"
    GET_REGISTRY_ACTIVITY_CREATE_AUTH_ROLES = "/registry/activity/create/auth/roles"
    GET_REGISTRY_ACTIVITY_CREATE_FETCH = "/registry/activity/create/fetch"
    GET_REGISTRY_ACTIVITY_CREATE_LOCKS_HISTORY = "/registry/activity/create/locks/history"
    GET_REGISTRY_ACTIVITY_CREATE_LOCKS_LOCKED = "/registry/activity/create/locks/locked"
    GET_REGISTRY_ACTIVITY_CREATE_SCHEMA = "/registry/activity/create/schema"
    GET_REGISTRY_ACTIVITY_CREATE_UI_SCHEMA = "/registry/activity/create/ui_schema"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_AUTH_CONFIGURATION = "/registry/activity/model_run/auth/configuration"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_AUTH_EVALUATE = "/registry/activity/model_run/auth/evaluate"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_AUTH_ROLES = "/registry/activity/model_run/auth/roles"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_FETCH = "/registry/activity/model_run/fetch"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_LOCKS_HISTORY = "/registry/activity/model_run/locks/history"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_LOCKS_LOCKED = "/registry/activity/model_run/locks/locked"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_SCHEMA = "/registry/activity/model_run/schema"
    GET_REGISTRY_ACTIVITY_MODEL_RUN_UI_SCHEMA = "/registry/activity/model_run/ui_schema"
    GET_REGISTRY_ACTIVITY_STUDY_AUTH_CONFIGURATION = "/registry/activity/study/auth/configuration"
    GET_REGISTRY_ACTIVITY_STUDY_AUTH_EVALUATE = "/registry/activity/study/auth/evaluate"
    GET_REGISTRY_ACTIVITY_STUDY_AUTH_ROLES = "/registry/activity/study/auth/roles"
    GET_REGISTRY_ACTIVITY_STUDY_FETCH = "/registry/activity/study/fetch"
    GET_REGISTRY_ACTIVITY_STUDY_LOCKS_HISTORY = "/registry/activity/study/locks/history"
    GET_REGISTRY_ACTIVITY_STUDY_LOCKS_LOCKED = "/registry/activity/study/locks/locked"
    GET_REGISTRY_ACTIVITY_STUDY_SCHEMA = "/registry/activity/study/schema"
    GET_REGISTRY_ACTIVITY_STUDY_UI_SCHEMA = "/registry/activity/study/ui_schema"
    GET_REGISTRY_ACTIVITY_VERSION_AUTH_CONFIGURATION = "/registry/activity/version/auth/configuration"
    GET_REGISTRY_ACTIVITY_VERSION_AUTH_EVALUATE = "/registry/activity/version/auth/evaluate"
    GET_REGISTRY_ACTIVITY_VERSION_AUTH_ROLES = "/registry/activity/version/auth/roles"
    GET_REGISTRY_ACTIVITY_VERSION_FETCH = "/registry/activity/version/fetch"
    GET_REGISTRY_ACTIVITY_VERSION_LOCKS_HISTORY = "/registry/activity/version/locks/history"
    GET_REGISTRY_ACTIVITY_VERSION_LOCKS_LOCKED = "/registry/activity/version/locks/locked"
    GET_REGISTRY_ACTIVITY_VERSION_SCHEMA = "/registry/activity/version/schema"
    GET_REGISTRY_ACTIVITY_VERSION_UI_SCHEMA = "/registry/activity/version/ui_schema"
    GET_REGISTRY_AGENT_ORGANISATION_AUTH_CONFIGURATION = "/registry/agent/organisation/auth/configuration"
    GET_REGISTRY_AGENT_ORGANISATION_AUTH_EVALUATE = "/registry/agent/organisation/auth/evaluate"
    GET_REGISTRY_AGENT_ORGANISATION_AUTH_ROLES = "/registry/agent/organisation/auth/roles"
    GET_REGISTRY_AGENT_ORGANISATION_FETCH = "/registry/agent/organisation/fetch"
    GET_REGISTRY_AGENT_ORGANISATION_LOCKS_HISTORY = "/registry/agent/organisation/locks/history"
    GET_REGISTRY_AGENT_ORGANISATION_LOCKS_LOCKED = "/registry/agent/organisation/locks/locked"
    GET_REGISTRY_AGENT_ORGANISATION_SCHEMA = "/registry/agent/organisation/schema"
    GET_REGISTRY_AGENT_ORGANISATION_UI_SCHEMA = "/registry/agent/organisation/ui_schema"
    GET_REGISTRY_AGENT_PERSON_AUTH_CONFIGURATION = "/registry/agent/person/auth/configuration"
    GET_REGISTRY_AGENT_PERSON_AUTH_EVALUATE = "/registry/agent/person/auth/evaluate"
    GET_REGISTRY_AGENT_PERSON_AUTH_ROLES = "/registry/agent/person/auth/roles"
    GET_REGISTRY_AGENT_PERSON_FETCH = "/registry/agent/person/fetch"
    GET_REGISTRY_AGENT_PERSON_LOCKS_HISTORY = "/registry/agent/person/locks/history"
    GET_REGISTRY_AGENT_PERSON_LOCKS_LOCKED = "/registry/agent/person/locks/locked"
    GET_REGISTRY_AGENT_PERSON_SCHEMA = "/registry/agent/person/schema"
    GET_REGISTRY_AGENT_PERSON_UI_SCHEMA = "/registry/agent/person/ui_schema"
    GET_REGISTRY_ENTITY_DATASET_AUTH_CONFIGURATION = "/registry/entity/dataset/auth/configuration"
    GET_REGISTRY_ENTITY_DATASET_AUTH_EVALUATE = "/registry/entity/dataset/auth/evaluate"
    GET_REGISTRY_ENTITY_DATASET_AUTH_ROLES = "/registry/entity/dataset/auth/roles"
    GET_REGISTRY_ENTITY_DATASET_FETCH = "/registry/entity/dataset/fetch"
    GET_REGISTRY_ENTITY_DATASET_LOCKS_HISTORY = "/registry/entity/dataset/locks/history"
    GET_REGISTRY_ENTITY_DATASET_LOCKS_LOCKED = "/registry/entity/dataset/locks/locked"
    GET_REGISTRY_ENTITY_DATASET_SCHEMA = "/registry/entity/dataset/schema"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_AUTH_CONFIGURATION = "/registry/entity/dataset_template/auth/configuration"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_AUTH_EVALUATE = "/registry/entity/dataset_template/auth/evaluate"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_AUTH_ROLES = "/registry/entity/dataset_template/auth/roles"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_FETCH = "/registry/entity/dataset_template/fetch"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_LOCKS_HISTORY = "/registry/entity/dataset_template/locks/history"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_LOCKS_LOCKED = "/registry/entity/dataset_template/locks/locked"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_SCHEMA = "/registry/entity/dataset_template/schema"
    GET_REGISTRY_ENTITY_DATASET_TEMPLATE_UI_SCHEMA = "/registry/entity/dataset_template/ui_schema"
    GET_REGISTRY_ENTITY_DATASET_UI_SCHEMA = "/registry/entity/dataset/ui_schema"
    GET_REGISTRY_ENTITY_MODEL_AUTH_CONFIGURATION = "/registry/entity/model/auth/configuration"
    GET_REGISTRY_ENTITY_MODEL_AUTH_EVALUATE = "/registry/entity/model/auth/evaluate"
    GET_REGISTRY_ENTITY_MODEL_AUTH_ROLES = "/registry/entity/model/auth/roles"
    GET_REGISTRY_ENTITY_MODEL_FETCH = "/registry/entity/model/fetch"
    GET_REGISTRY_ENTITY_MODEL_LOCKS_HISTORY = "/registry/entity/model/locks/history"
    GET_REGISTRY_ENTITY_MODEL_LOCKS_LOCKED = "/registry/entity/model/locks/locked"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_AUTH_CONFIGURATION = "/registry/entity/model_run_workflow/auth/configuration"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_AUTH_EVALUATE = "/registry/entity/model_run_workflow/auth/evaluate"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_AUTH_ROLES = "/registry/entity/model_run_workflow/auth/roles"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_FETCH = "/registry/entity/model_run_workflow/fetch"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_LOCKS_HISTORY = "/registry/entity/model_run_workflow/locks/history"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_LOCKS_LOCKED = "/registry/entity/model_run_workflow/locks/locked"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_SCHEMA = "/registry/entity/model_run_workflow/schema"
    GET_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_UI_SCHEMA = "/registry/entity/model_run_workflow/ui_schema"
    GET_REGISTRY_ENTITY_MODEL_SCHEMA = "/registry/entity/model/schema"
    GET_REGISTRY_ENTITY_MODEL_UI_SCHEMA = "/registry/entity/model/ui_schema"
    GET_REGISTRY_GENERAL_ABOUT_VERSION = "/registry/general/about/version"
    GET_REGISTRY_GENERAL_FETCH = "/registry/general/fetch"
    POST_REGISTRY_ACTIVITY_CREATE_LIST = "/registry/activity/create/list"
    POST_REGISTRY_ACTIVITY_CREATE_VALIDATE = "/registry/activity/create/validate"
    POST_REGISTRY_ACTIVITY_MODEL_RUN_LIST = "/registry/activity/model_run/list"
    POST_REGISTRY_ACTIVITY_MODEL_RUN_VALIDATE = "/registry/activity/model_run/validate"
    POST_REGISTRY_ACTIVITY_STUDY_CREATE = "/registry/activity/study/create"
    POST_REGISTRY_ACTIVITY_STUDY_LIST = "/registry/activity/study/list"
    POST_REGISTRY_ACTIVITY_STUDY_SEED = "/registry/activity/study/seed"
    POST_REGISTRY_ACTIVITY_STUDY_VALIDATE = "/registry/activity/study/validate"
    POST_REGISTRY_ACTIVITY_VERSION_LIST = "/registry/activity/version/list"
    POST_REGISTRY_ACTIVITY_VERSION_VALIDATE = "/registry/activity/version/validate"
    POST_REGISTRY_AGENT_ORGANISATION_CREATE = "/registry/agent/organisation/create"
    POST_REGISTRY_AGENT_ORGANISATION_LIST = "/registry/agent/organisation/list"
    POST_REGISTRY_AGENT_ORGANISATION_SEED = "/registry/agent/organisation/seed"
    POST_REGISTRY_AGENT_ORGANISATION_VALIDATE = "/registry/agent/organisation/validate"
    POST_REGISTRY_AGENT_PERSON_CREATE = "/registry/agent/person/create"
    POST_REGISTRY_AGENT_PERSON_LIST = "/registry/agent/person/list"
    POST_REGISTRY_AGENT_PERSON_SEED = "/registry/agent/person/seed"
    POST_REGISTRY_AGENT_PERSON_VALIDATE = "/registry/agent/person/validate"
    POST_REGISTRY_ENTITY_DATASET_LIST = "/registry/entity/dataset/list"
    POST_REGISTRY_ENTITY_DATASET_TEMPLATE_CREATE = "/registry/entity/dataset_template/create"
    POST_REGISTRY_ENTITY_DATASET_TEMPLATE_LIST = "/registry/entity/dataset_template/list"
    POST_REGISTRY_ENTITY_DATASET_TEMPLATE_SEED = "/registry/entity/dataset_template/seed"
    POST_REGISTRY_ENTITY_DATASET_TEMPLATE_VALIDATE = "/registry/entity/dataset_template/validate"
    POST_REGISTRY_ENTITY_DATASET_TEMPLATE_VERSION = "/registry/entity/dataset_template/version"
    POST_REGISTRY_ENTITY_DATASET_USER_RELEASES = "/registry/entity/dataset/user/releases"
    POST_REGISTRY_ENTITY_DATASET_VALIDATE = "/registry/entity/dataset/validate"
    POST_REGISTRY_ENTITY_MODEL_CREATE = "/registry/entity/model/create"
    POST_REGISTRY_ENTITY_MODEL_LIST = "/registry/entity/model/list"
    POST_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_CREATE = "/registry/entity/model_run_workflow/create"
    POST_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_LIST = "/registry/entity/model_run_workflow/list"
    POST_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_SEED = "/registry/entity/model_run_workflow/seed"
    POST_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_VALIDATE = "/registry/entity/model_run_workflow/validate"
    POST_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_VERSION = "/registry/entity/model_run_workflow/version"
    POST_REGISTRY_ENTITY_MODEL_SEED = "/registry/entity/model/seed"
    POST_REGISTRY_ENTITY_MODEL_VALIDATE = "/registry/entity/model/validate"
    POST_REGISTRY_ENTITY_MODEL_VERSION = "/registry/entity/model/version"
    POST_REGISTRY_GENERAL_LIST = "/registry/general/list"
    PUT_REGISTRY_ACTIVITY_CREATE_AUTH_CONFIGURATION = "/registry/activity/create/auth/configuration"
    PUT_REGISTRY_ACTIVITY_CREATE_LOCKS_LOCK = "/registry/activity/create/locks/lock"
    PUT_REGISTRY_ACTIVITY_CREATE_LOCKS_UNLOCK = "/registry/activity/create/locks/unlock"
    PUT_REGISTRY_ACTIVITY_MODEL_RUN_AUTH_CONFIGURATION = "/registry/activity/model_run/auth/configuration"
    PUT_REGISTRY_ACTIVITY_MODEL_RUN_LOCKS_LOCK = "/registry/activity/model_run/locks/lock"
    PUT_REGISTRY_ACTIVITY_MODEL_RUN_LOCKS_UNLOCK = "/registry/activity/model_run/locks/unlock"
    PUT_REGISTRY_ACTIVITY_STUDY_AUTH_CONFIGURATION = "/registry/activity/study/auth/configuration"
    PUT_REGISTRY_ACTIVITY_STUDY_LOCKS_LOCK = "/registry/activity/study/locks/lock"
    PUT_REGISTRY_ACTIVITY_STUDY_LOCKS_UNLOCK = "/registry/activity/study/locks/unlock"
    PUT_REGISTRY_ACTIVITY_STUDY_REVERT = "/registry/activity/study/revert"
    PUT_REGISTRY_ACTIVITY_STUDY_UPDATE = "/registry/activity/study/update"
    PUT_REGISTRY_ACTIVITY_VERSION_AUTH_CONFIGURATION = "/registry/activity/version/auth/configuration"
    PUT_REGISTRY_ACTIVITY_VERSION_LOCKS_LOCK = "/registry/activity/version/locks/lock"
    PUT_REGISTRY_ACTIVITY_VERSION_LOCKS_UNLOCK = "/registry/activity/version/locks/unlock"
    PUT_REGISTRY_AGENT_ORGANISATION_AUTH_CONFIGURATION = "/registry/agent/organisation/auth/configuration"
    PUT_REGISTRY_AGENT_ORGANISATION_LOCKS_LOCK = "/registry/agent/organisation/locks/lock"
    PUT_REGISTRY_AGENT_ORGANISATION_LOCKS_UNLOCK = "/registry/agent/organisation/locks/unlock"
    PUT_REGISTRY_AGENT_ORGANISATION_REVERT = "/registry/agent/organisation/revert"
    PUT_REGISTRY_AGENT_ORGANISATION_UPDATE = "/registry/agent/organisation/update"
    PUT_REGISTRY_AGENT_PERSON_AUTH_CONFIGURATION = "/registry/agent/person/auth/configuration"
    PUT_REGISTRY_AGENT_PERSON_LOCKS_LOCK = "/registry/agent/person/locks/lock"
    PUT_REGISTRY_AGENT_PERSON_LOCKS_UNLOCK = "/registry/agent/person/locks/unlock"
    PUT_REGISTRY_AGENT_PERSON_REVERT = "/registry/agent/person/revert"
    PUT_REGISTRY_AGENT_PERSON_UPDATE = "/registry/agent/person/update"
    PUT_REGISTRY_ENTITY_DATASET_AUTH_CONFIGURATION = "/registry/entity/dataset/auth/configuration"
    PUT_REGISTRY_ENTITY_DATASET_LOCKS_LOCK = "/registry/entity/dataset/locks/lock"
    PUT_REGISTRY_ENTITY_DATASET_LOCKS_UNLOCK = "/registry/entity/dataset/locks/unlock"
    PUT_REGISTRY_ENTITY_DATASET_TEMPLATE_AUTH_CONFIGURATION = "/registry/entity/dataset_template/auth/configuration"
    PUT_REGISTRY_ENTITY_DATASET_TEMPLATE_LOCKS_LOCK = "/registry/entity/dataset_template/locks/lock"
    PUT_REGISTRY_ENTITY_DATASET_TEMPLATE_LOCKS_UNLOCK = "/registry/entity/dataset_template/locks/unlock"
    PUT_REGISTRY_ENTITY_DATASET_TEMPLATE_REVERT = "/registry/entity/dataset_template/revert"
    PUT_REGISTRY_ENTITY_DATASET_TEMPLATE_UPDATE = "/registry/entity/dataset_template/update"
    PUT_REGISTRY_ENTITY_MODEL_AUTH_CONFIGURATION = "/registry/entity/model/auth/configuration"
    PUT_REGISTRY_ENTITY_MODEL_LOCKS_LOCK = "/registry/entity/model/locks/lock"
    PUT_REGISTRY_ENTITY_MODEL_LOCKS_UNLOCK = "/registry/entity/model/locks/unlock"
    PUT_REGISTRY_ENTITY_MODEL_REVERT = "/registry/entity/model/revert"
    PUT_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_AUTH_CONFIGURATION = "/registry/entity/model_run_workflow/auth/configuration"
    PUT_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_LOCKS_LOCK = "/registry/entity/model_run_workflow/locks/lock"
    PUT_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_LOCKS_UNLOCK = "/registry/entity/model_run_workflow/locks/unlock"
    PUT_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_REVERT = "/registry/entity/model_run_workflow/revert"
    PUT_REGISTRY_ENTITY_MODEL_RUN_WORKFLOW_UPDATE = "/registry/entity/model_run_workflow/update"
    PUT_REGISTRY_ENTITY_MODEL_UPDATE = "/registry/entity/model/update"

class RegistryAdminEndpoints(str, Enum):
    GET_ADMIN_CONFIG = "/admin/config"
    GET_ADMIN_EXPORT = "/admin/export"
    GET_ADMIN_SENTRY_DEBUG = "/admin/sentry-debug"
    POST_ADMIN_IMPORT = "/admin/import"
    POST_ADMIN_RESTORE_FROM_TABLE = "/admin/restore_from_table"

"""    

# L2 interface.

class RegistryClient(ClientService):
    def __init__(self, auth: AuthManager, config: Config) -> None:
        """Initialises the RegistryClient with authentication and configuration.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow method.
        config : Config
            A config object which contains information related to the Provena instance.
        """ 
        self._auth = auth       
        self._config = config


    # Function to get the endpoint URL
    def _build_endpoint(self, action: Action, item_subtype: ItemSubType) -> str:
        subtype_prefix = subtype_route_prefixes[item_subtype]
        action_postfix = action_postfixes[action]
        return f"{self._config.registry_api_endpoint}{subtype_prefix}{action_postfix}"