# read version from installed package
from importlib.metadata import version
__version__ = version("provenaclient")

from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.utils.config import Config, EndpointConfig

import ProvenaInterfaces as interfaces