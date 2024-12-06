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
from pydantic import BaseModel, ValidationError, validator
from ProvenaInterfaces.ProvenanceAPI import LineageResponse
from ProvenaInterfaces.RegistryAPI import Node

class HealthCheckResponse(BaseModel):
    message: str

class AsyncAwaitSettings(BaseModel):
    # polling interval in seconds (defaults to 2 seconds)
    job_polling_interval : int = 2
        
    # how long do we wait for the entry to be present in table? (seconds)
    job_async_queue_delay_polling_timeout = 20  # 20 seconds

    # how long do we wait for it to leave pending? (seconds)
    job_async_pending_polling_timeout = 120  # 2 minutes

    # how long do we wait for it to become in progress? (seconds)
    job_async_in_progress_polling_timeout = 180  # 3 minutes
   
DEFAULT_AWAIT_SETTINGS = AsyncAwaitSettings()


class CustomGraph(BaseModel): 
    directed: bool
    multigraph: bool
    graph: Dict[str, Any]
    nodes: List[Node] 
    
class CustomLineageResponse(LineageResponse): 
    """A Custom Lineage Response Pydantic Model 
    that inherits from its parent (LineageResponse). 

    This model overrides the "graph" field within the 
    Lineage Response, and converts it from an untyped 
    dictionary into a pydantic object/ typed datatype. 

    The custom validator function is called, and has custom 
    parsing logic to parse the nodes as well.

    """

    graph: Optional[CustomGraph] #type:ignore

    @validator('graph')
    @classmethod
    def convert_graph(cls: Type["CustomLineageResponse"], v: Dict[str, Any]) -> Optional[CustomGraph]:
        """Converts the untyped "graph" dictionary into a typed pydantic object/ datatype. 

        Parameters
        ----------
        cls : Type[CustomLineageResponse]
        v : Dict[str, Any]
            The "graph" untyped dictionary from Lineage Response. 

        Returns
        -------
        Optional[CustomGraph]
            Pydantic object that is formed from the untyped dictionary.
        """

        if v is None:
            return None
        
        # Parse the nodes before returning the pydantic object 
        list_of_parsed_nodes: List[Node] = cls.parse_nodes(v.get('nodes', []))

        # Convert the generic dict to CustomGraph structure
        return CustomGraph(
                directed= v.get('directed', False),
                multigraph= v.get('multigraph', False),
                graph= v.get('graph', {}), 
                nodes= list_of_parsed_nodes
            )
    
    @classmethod
    def parse_nodes(cls, nodes_to_parse: List[Any]) -> List[Node]: 
        """Parses potential nodes into typed node objects.

        Parameters
        ----------
        nodes_to_parse : List[Any]
            A list of potential nodes.

        Returns
        -------
        List[Node]
            A list of typed nodes.

        Raises
        ------
        ValidationError
            Raised when node parsing fails.
        Exception
            Raised for any error that occurs during parsing of the node.
        """

        try:
            nodes_parsed_list: List[Node] = []
            
            for node in nodes_to_parse:
                parsed_node = Node.parse_obj(node)
                nodes_parsed_list.append(parsed_node)

            return nodes_parsed_list
        
        except ValidationError as e: 
            raise ValidationError(f"Something has gone with parsing the nodes - {e}", model=Node)

        except Exception as e: 
            raise Exception(f"Something has gone wrong with parsing the node - {e}")