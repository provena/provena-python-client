
from datetime import date
from dataclasses import dataclass
from typing import cast
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.SearchAPI import *
from ProvenaInterfaces.ProvenanceAPI import * 
from ProvenaInterfaces.ProvenanceModels import *
from ProvenaInterfaces.AsyncJobModels import *

from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.utils.registry_endpoints import *
from provenaclient.modules import Registry
from test_config import RouteParameters, route_params, non_test_route_params
from ProvenaInterfaces.AsyncJobModels import RegistryRegisterCreateActivityResult


CLEANUP_ITEMS = List[Tuple[ItemSubType, IdentifiedResource]]


async def create_item(client: ProvenaClient, item_subtype: ItemSubType) -> Optional[GenericCreateResponse]:

    if item_subtype == ItemSubType.ORGANISATION:
        example_org_domain_info = get_item_subtype_domain_info_example(item_subtype=item_subtype)
        example_org_domain_info = cast(OrganisationDomainInfo, example_org_domain_info)

        created_org = await client.registry.organisation.create_item(create_item_request=example_org_domain_info)
        return created_org
    
    if item_subtype == ItemSubType.PERSON:
        example_person_domain_info = get_item_subtype_domain_info_example(item_subtype=item_subtype)
        example_person_domain_info = cast(PersonDomainInfo, example_person_domain_info)

        created_person = await client.registry.person.create_item(create_item_request=example_person_domain_info)
        return created_person
    
    if item_subtype == ItemSubType.STUDY:
        example_study_domain_info = get_item_subtype_domain_info_example(item_subtype=item_subtype)
        example_study_domain_info = cast(PersonDomainInfo, example_study_domain_info)

        created_study = await client.registry.person.create_item(create_item_request=example_study_domain_info)
        return created_study
    
    if item_subtype == ItemSubType.MODEL:
        example_model_domain_info = get_item_subtype_domain_info_example(item_subtype=item_subtype)
        example_model_domain_info = cast(ModelDomainInfo, example_model_domain_info)

        created_model = await client.registry.model.create_item(create_item_request=example_model_domain_info)
        return created_model
    
    if item_subtype == ItemSubType.DATASET_TEMPLATE:
        example_dataset_template_domain_info = get_item_subtype_domain_info_example(item_subtype=item_subtype)
        example_dataset_template_domain_info = cast(DatasetTemplateDomainInfo, example_dataset_template_domain_info)

        created_dataset_template = await client.registry.dataset_template.create_item(create_item_request=example_dataset_template_domain_info)
        return created_dataset_template

    return None

async def create_item_from_domain_info_successfully(client: ProvenaClient, item_subtype: ItemSubType, domain_info: DomainInfoBase) -> Optional[GenericCreateResponse]:

    if item_subtype == ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE:
        domain_info = cast(ModelRunWorkflowTemplateDomainInfo, domain_info)
        created_model_run_workflow_template = await client.registry.model_run_workflow.create_item(create_item_request=domain_info)
        return created_model_run_workflow_template

        
    return None

async def register_model_run_successfully(client: ProvenaClient, model_run_record: ModelRunRecord) -> ProvenanceRecordInfo:

    registered_model_run = await client.prov_api.register_model_run(model_run_payload=model_run_record)
    assert registered_model_run is not None, f"Model run record is None or Null"
    assert registered_model_run.status.success, f"Model run registration failed with details {registered_model_run.status.details}"

    session_id = registered_model_run.session_id
    assert session_id

    payload = await client.job_api.await_successful_job_completion(session_id=session_id)
    assert payload.status == JobStatus.SUCCEEDED, f"Expected successful prov lodge but had status {payload.status}. Info: {payload.info or 'None provided'}"

    # parse the result payload from job status
    result = ProvLodgeModelRunResult.parse_obj(payload.result)

    assert result.record.record, "Recieved no record in record info to register model run."
    return result.record



async def cleanup_helper(client: ProvenaClient, list_of_handles: CLEANUP_ITEMS) -> None:
    for item_sub_type, handle in list_of_handles:
        delete_status_response = await client.registry.admin.delete(id=handle, item_subtype=item_sub_type)
        assert delete_status_response.status.success, f"Delete request has failed with details {delete_status_response.status.details}."

async def cleanup_create_activity_from_item_base(client: ProvenaClient, item: ItemBase, cleanup_items: CLEANUP_ITEMS) -> None:
    assert item.item_category == ItemCategory.ENTITY, f"Cleaning up registry create for non Entity will freeze because no such item exists"
    if item.workflow_links is not None and\
            item.workflow_links.create_activity_workflow_id is not None:
        # Ensure the workflow links were updated

        # wait for the complete lifecycle - step 1
        create_response = await client.job_api.await_successful_job_completion(
            session_id=item.workflow_links.create_activity_workflow_id,
        )

        assert create_response.result is not None
        parsed_result = RegistryRegisterCreateActivityResult.parse_obj(
            create_response.result)
        creation_activity_id = parsed_result.creation_activity_id
        
        cleanup_items.append(
            (ItemSubType.CREATE, creation_activity_id))


def get_item_subtype_route_params(item_subtype: ItemSubType) -> RouteParameters:
    """Given an item subtype, will source a its RouteParmeters
    Parameters
    ----------
    item_subtype : ItemSubType
        The desired Item subtype to source route parameters for
    Returns
    -------
    RouteParameters
        the routeparametrs for the desired item subtype
    """
    for item_route_params in route_params:
        if item_route_params.subtype == item_subtype:
            return item_route_params

    for item_route_params in non_test_route_params:
        if item_route_params.subtype == item_subtype:
            return item_route_params

    raise Exception(
        f"Was not able to source route parameters for desired item_subtype = {item_subtype}")


def get_item_subtype_domain_info_example(item_subtype: ItemSubType) -> DomainInfoBase:
    # may require re parsing of results with correct type outside of this to obtain full access to fields.
    return get_item_subtype_route_params(item_subtype=item_subtype).model_examples.domain_info[0]
    

Graph = Dict[str, Any]

@dataclass
class GraphProperty():
    type: str
    source: str
    target: str


def assert_graph_property(prop: GraphProperty, graph: Graph) -> None:
    """

    Determines if the desired graph property exists in the networkX JSON graph
    in the graph object.

    Uses assertions to raise an assertion error if the property is not present.

    Args:
        prop (GraphProperty): The desired property 

        graph (Graph): The graph to analyse
    """

    links = graph['links']
    found = False
    for l in links:
        actual_prop = GraphProperty(**l)
        if actual_prop == prop:
            found = True
            break

    assert found, f"Could not find relation specified {prop}."


def assert_non_empty_graph_property(prop: GraphProperty, lineage_response: LineageResponse) -> None:
    """
    Determines if the desired graph property exists in the networkX JSON graph
    lineage response in the graph object.

    Uses assertions to raise an assertion error if the property is not present.

    Args:
        prop (GraphProperty): The desired property 

        graph (Graph): The graph to analyse
    """
    g = lineage_response.graph
    assert g is not None, f"Empty graph when non empty graph was expected."
    assert_graph_property(prop=prop, graph=g)
