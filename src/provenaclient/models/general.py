'''
Created Date: Monday June 17th 2024 +1000
Author: Peter Baker
-----
Last Modified: Monday June 17th 2024 4:45:39 pm +1000
Modified By: Peter Baker
-----
Description: General interfaces defined to help with typing the client library/configuring
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''

from typing import Any, Dict, Optional, Type, TypedDict, List
from pydantic import AliasChoices, BaseModel, Field, ValidationError, validator
from ProvenaInterfaces.RegistryAPI import ItemSubType, Node
from ProvenaInterfaces.ProvenanceAPI import LineageResponse


class HealthCheckResponse(BaseModel):
    message: str


class AsyncAwaitSettings(BaseModel):
    # polling interval in seconds (defaults to 2 seconds)
    job_polling_interval: int = 2

    # how long do we wait for the entry to be present in table? (seconds)
    job_async_queue_delay_polling_timeout: int = 20  # 20 seconds

    # how long do we wait for it to leave pending? (seconds)
    job_async_pending_polling_timeout: int = 120  # 2 minutes

    # how long do we wait for it to become in progress? (seconds)
    job_async_in_progress_polling_timeout : int = 180  # 3 minutes


DEFAULT_AWAIT_SETTINGS = AsyncAwaitSettings()


class GraphProperty(BaseModel):
    type: str
    source: str
    target: str


class CustomGraph(BaseModel):
    """NetworkX node-link style graph.

    The provenance API returns ``graph`` as JSON. Edges are normally under ``links``
    (NetworkX ``node_link_data``). If the service uses another key (e.g. ``edges``),
    we still populate ``links`` so the client matches NetworkX conventions.

    If ``links`` is missing and no alias matches, it defaults to ``[]`` — compare the
    raw ``LineageResponse.graph`` keys using ``scripts/diagnose_lineage_graph.py``
    to see whether the API omitted edges or used an unsupported key.
    """

    directed: bool
    multigraph: bool
    graph: Dict[str, Any]
    nodes: List[Node] = Field(default_factory=list)
    links: List[GraphProperty] = Field(
        default_factory=list,
        validation_alias=AliasChoices("links", "edges"),
    )


class CustomLineageResponse(LineageResponse):
    """A Custom Lineage Response Pydantic Model 
    that inherits from its parent (LineageResponse). 

    This model overrides the "graph" field within the 
    Lineage Response, and converts it from an untyped 
    dictionary into a pydantic object/ typed datatype. 

    The custom validator function is called, and has custom 
    parsing logic to parse the nodes as well.

    """

    graph: Optional[CustomGraph]  # type:ignore
