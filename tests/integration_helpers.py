
from dataclasses import dataclass
from pathlib import Path
import time
import os
from typing import cast

from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.SearchAPI import *
from ProvenaInterfaces.ProvenanceAPI import *
from ProvenaInterfaces.ProvenanceModels import *
from ProvenaInterfaces.AsyncJobModels import *
from ProvenaInterfaces.TestConfig import RouteParameters, route_params, non_test_route_params
from ProvenaInterfaces.AsyncJobModels import RegistryRegisterCreateActivityResult

from provenaclient.models.general import CustomGraph, CustomLineageResponse, GraphProperty
from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.modules.registry import ModelClient, OrganisationClient, PersonClient, StudyClient, DatasetTemplateClient
from provenaclient.utils.registry_endpoints import *


# Alias for cleanup items list
CLEANUP_ITEMS = List[Tuple[ItemSubType, IdentifiedResource]]
# Alias for all the registry clients (These clients can create entities through their create_item method)
ENTITY_CREATING_REGISTRY_CLIENTS = Union[OrganisationClient, PersonClient, StudyClient, ModelClient, DatasetTemplateClient]


async def create_item(client: ProvenaClient, item_subtype: ItemSubType) -> ItemBase:
    """
    Create an item of the specified subtype.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    item_subtype : ItemSubType
        The subtype of the item to create.

    Returns
    -------
    Optional[GenericCreateResponse]
        The response from the create item request, or None if the subtype is not handled.
    """

    domain_info_mapping: Dict[ItemSubType, Type[DomainInfoBase]] = {
        ItemSubType.ORGANISATION: OrganisationDomainInfo,
        ItemSubType.PERSON: PersonDomainInfo,
        ItemSubType.STUDY: StudyDomainInfo,
        ItemSubType.MODEL: ModelDomainInfo,
        ItemSubType.DATASET_TEMPLATE: DatasetTemplateDomainInfo
    }

    # Mapping of item subtypes to their respective subclients
    subtype_to_subclient: Dict[ItemSubType, ENTITY_CREATING_REGISTRY_CLIENTS] = {
        ItemSubType.ORGANISATION: client.registry.organisation,
        ItemSubType.PERSON: client.registry.person,
        ItemSubType.STUDY: client.registry.study,
        ItemSubType.MODEL: client.registry.model,
        ItemSubType.DATASET_TEMPLATE: client.registry.dataset_template
    }

    domain_info = get_item_subtype_domain_info_example(
        item_subtype=item_subtype)

    # Cast the domain info to the appropriate type
    domain_info_type = domain_info_mapping[item_subtype]
    specific_domain_info = cast(domain_info_type, domain_info)  # type:ignore

    # Get the subclient and create the item
    subclient = subtype_to_subclient[item_subtype]
    created_item = await subclient.create_item(create_item_request=specific_domain_info)

    asserted_created_item = assert_created_item(
        item=created_item, item_subtype=item_subtype)

    # Return Itembase
    return asserted_created_item


async def create_item_from_domain_info_successfully(client: ProvenaClient, item_subtype: ItemSubType, domain_info: DomainInfoBase) -> Optional[GenericCreateResponse]:
    """
    Create an item from the given domain information.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    item_subtype : ItemSubType
        The subtype of the item to create.
    domain_info : DomainInfoBase
        The domain information for the item to be created.

    Returns
    -------
    Optional[GenericCreateResponse]
        The response from the create item request, or None if the subtype is not handled.
    """

    if item_subtype == ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE:
        domain_info = cast(ModelRunWorkflowTemplateDomainInfo, domain_info)
        created_model_run_workflow_template = await client.registry.model_run_workflow.create_item(create_item_request=domain_info)
        return created_model_run_workflow_template

    return None


async def register_model_run_successfully(client: ProvenaClient, model_run_record: ModelRunRecord) -> ProvenanceRecordInfo:
    """
    Register a model run successfully and verify the registration process.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    model_run_record : ModelRunRecord
        The model run record to be registered.

    Returns
    -------
    ProvenanceRecordInfo
        The provenance record information after successful registration.
    """

    registered_model_run = await client.prov_api.register_model_run(model_run_payload=model_run_record)
    assert registered_model_run is not None, "Model run record is None or Null"
    assert registered_model_run.status.success, f"Model run registration failed with details {registered_model_run.status.details}"

    session_id = registered_model_run.session_id
    assert session_id

    payload = await client.job_api.await_successful_job_completion(session_id=session_id)
    assert payload.status == JobStatus.SUCCEEDED, f"Expected successful prov lodge but had status {payload.status}. Info: {payload.info or 'None provided'}"

    # parse the result payload from job status
    result = ProvLodgeModelRunResult.parse_obj(payload.result)

    assert result.record.record, "Received no record in record info to register model run."
    return result.record


async def register_model_run_failure(client: ProvenaClient, model_run_record: ModelRunRecord) -> ProvenanceRecordInfo:
    """
    Register a model run and verify that the registration fails.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    model_run_record : ModelRunRecord
        The model run record to be registered.

    Returns
    -------
    ProvenanceRecordInfo
        The provenance record information after registration failure.
    """

    registered_model_run = await client.prov_api.register_model_run(model_run_payload=model_run_record)
    assert registered_model_run is not None, "Model run record is None or Null"
    assert not registered_model_run.status.success, f"Model run registration unexpectedly succeeded with details {registered_model_run.status.details}"

    session_id = registered_model_run.session_id
    assert session_id

    payload = await client.job_api.await_successful_job_completion(session_id=session_id)
    assert payload.status == JobStatus.FAILED, f"Expected failed prov lodge but had status {payload.status}. Info: {payload.info or 'None provided'}"

    # parse the result payload from job status
    result = ProvLodgeModelRunResult.parse_obj(payload.result)

    assert result.record.record, "Received no record in record info for failed model run."
    return result.record


async def cleanup_helper(client: ProvenaClient, list_of_handles: CLEANUP_ITEMS) -> None:
    """
    Cleanup items from the registry based on their handles.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    list_of_handles : CLEANUP_ITEMS
        A list of tuples containing item subtypes and handles to be deleted.
    """

    for item_sub_type, handle in list_of_handles:
        delete_status_response = await client.registry.admin.delete(id=handle, item_subtype=item_sub_type)
        assert delete_status_response.status.success, f"Delete request has failed with details {delete_status_response.status.details}."


def assert_created_item(item: GenericCreateResponse, item_subtype: ItemSubType) -> ItemBase:
    """
    Asserts that the item was created successfully.

    Parameters
    ----------
    item : GenericCreateResponse
        The created entity to be asserted.
    item_subtype : ItemSubType
        The subtype of the item.
    """
    assert item, f"The {item_subtype.name} is null or none."
    assert item.created_item, f"Created {item_subtype.name} does not contain a created item field."
    assert item.created_item.id, f"Created {item_subtype.name} does not contain a handle ID."

    if item.status:
        assert item.status.success, f"Reported failure when creating {item_subtype.name} with the following details\
                                    {item.status.details}"

    return item.created_item


def assert_list_items(item: GenericListResponse, item_subtype: ItemSubType) -> List[Any]:

    assert item, f"The {item_subtype.name} list response is null or none."
    assert item.items, f"The {item_subtype.name} list response did not contain a items field."

    if item.status:
        assert item.status.success, f"The {item_subtype.name} list failed to create with the following error \
                                    {item.status.details} "

    return item.items


async def search_and_assert(client: ProvenaClient, item_id: str, item_subtype: ItemSubType, sleep_time: int = 10) -> None:
    """Search for an item and assert that it exists in the search results. If the item was just created, it may be necessary to wait for the search index to update
    by supplying a non-zero sleep time, or calling a time.sleep() before this function if there was a list of entities created and searching
    is occuring all at the end.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    item_id : str
        item handle to search for
    item_subtype : ItemSubType
        item subtype of the item to search for
    sleep_time : int, optional
        Sleep time to allow for search api to index, by default 10. Set to 0 and use your own sleep as well.

    Raises
    ------
    AssertionError
        If the search fails to find the item in the search results. This could be
        likely because the search API is yet to index the item.
    """
    # Sleep for 10 seconds, so search api can fairly detect created entity.
    time.sleep(sleep_time)

    search_response = await client.search.search_registry(query=item_id, subtype_filter=item_subtype, limit=None)
    assert search_response.status.success, f"Search failed for {item_subtype.name} with handle {item_id}"
    assert search_response.results, f"No results found for {item_subtype.name} with handle {item_id}"
    search_result_ids = [result.id for result in search_response.results]
    if item_id not in search_result_ids:
        raise AssertionError(
            f"Search failed to find {item_subtype.name} with handle {item_id} inside search results. Search result IDs: {search_result_ids}")


async def cleanup_create_activity_from_item_base(client: ProvenaClient, item: ItemBase, cleanup_items: CLEANUP_ITEMS) -> None:
    """
    Cleanup the create activity from an item base, ensuring the workflow lifecycle is complete.

    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    item : ItemBase
        The item base from which the create activity needs to be cleaned up.
    cleanup_items : CLEANUP_ITEMS
        A list to append the items that need to be cleaned up.
    """

    assert item.item_category == ItemCategory.ENTITY, "Cleaning up registry create for non Entity will freeze because no such item exists"
    if item.workflow_links is not None and item.workflow_links.create_activity_workflow_id is not None:
        # Ensure the workflow links were updated

        # wait for the complete lifecycle - step 1
        create_response = await client.job_api.await_successful_job_completion(
            session_id=item.workflow_links.create_activity_workflow_id,
        )

        assert create_response.result is not None
        parsed_result = RegistryRegisterCreateActivityResult.parse_obj(
            create_response.result)
        creation_activity_id = parsed_result.creation_activity_id

        cleanup_items.append((ItemSubType.CREATE, creation_activity_id))


async def clear_all_links_with_person_id_user(client: ProvenaClient, person_id: str) -> None:
    """Clear all user personID links associated with the user associated with the person ID.


    Parameters
    ----------
    client : ProvenaClient
        The ProvenaClient instance used to interact with the API.
    person_id : str
        The person ID for which all links need to be cleared.
    """
    username_lookup_resp = await client.auth_api.admin.get_link_reverse_lookup_username(person_id=person_id)
    for username in username_lookup_resp.usernames:
        await client.auth_api.admin.delete_clear_link(username=username)


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
    """Reterives an item from the pre-loaded complete/dummy examples.

    Parameters
    ----------
    item_subtype : ItemSubType
        The desired Item subtype to source route parameters for

    Returns
    -------
    DomainInfoBase
        All domain information required for that entity/subtype.
    """
    # may require re parsing of results with correct type outside of this to obtain full access to fields.
    return get_item_subtype_route_params(item_subtype=item_subtype).model_examples.domain_info[0]


Graph = CustomGraph


def assert_graph_property(prop: GraphProperty, graph: Graph) -> None:
    """

    Determines if the desired graph property exists in the networkX JSON graph
    in the graph object.

    Uses assertions to raise an assertion error if the property is not present.

    Args:
        prop (GraphProperty): The desired property 

        graph (Graph): The graph to analyse
    """

    links = graph.links
    found = False
    for l in links:
        actual_prop = GraphProperty(type=l.type, source=l.source, target=l.target)
        if actual_prop == prop: 
            found = True
            break
    
    assert found, f"Could not find relation specified {prop}."

def assert_non_empty_graph_property(prop: GraphProperty, lineage_response: CustomLineageResponse) -> None:
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


# Below function not in use, but I see it being useful potentially later on for extensive testing if needed.
# Inspired from: https://stackoverflow.com/a/19308592
def get_filepaths(directory: str)  -> List[str]: 
    """This function gets all files and sub-directories within a directory.
    You can utilise this to compare contents between two directories. 

    Parameters
    ----------
    directory : str
        Path of a directory.

    Returns
    -------
    List[str]
        A list of all files/folders represented in the following format: 
        E.g: [textfile.txt, subfolder/textfile1.txt]
    """
    
    file_paths = []
    base_dir = Path(directory)

    for root,_,files in os.walk(directory):
        for filename in files: 
            # Extracts relative path
            filepath = os.path.relpath(os.path.join(root,filename), base_dir)
            file_paths.append(filepath)
    
    # Returning this sorted for faster comparison.
    return sorted(file_paths) 
