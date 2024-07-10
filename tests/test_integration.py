'''
Created Date: Wednesday June 26th 2024 +0000
Author: Parth Kuulkarni
-----
Last Modified: Wednesday June 26th 2024 3:16:19 PM +0000
Modified By: Parth Kulkarni
-----
Description: TODO
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
10-07-2024 | Parth Kulkarni | In Progress of Integration Testing. 

'''

from typing import Any, AsyncGenerator, List, cast
import pytest
import pytest_asyncio
import httpx

from provenaclient.auth import DeviceFlow
from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.modules.registry import Registry
from provenaclient.utils.config import Config

from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.AsyncJobModels import RegistryRegisterCreateActivityResult

from integration_helpers import *
from provenaclient.utils.exceptions import BadRequestException
import time

"""Pre-requiests before running unit tests: 

   1. You will need to setup token flow to be able to run these tests.
      For now I will use my tokens through device flow. 
   2. Creating various helper functions.

"""


"""Registering and Finding Dataset"""

@pytest.fixture(scope="session")
def auth_manager() -> DeviceFlow:

    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    return DeviceFlow(config=config, client_id="client-tools")

@pytest.fixture(scope="session")
def client(auth_manager: DeviceFlow) -> ProvenaClient:
    
    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    return ProvenaClient(config=config, auth=auth_manager)

@pytest_asyncio.fixture(scope="session")
async def cleanup_items(client: ProvenaClient) -> AsyncGenerator[CLEANUP_ITEMS, None]:
    items: CLEANUP_ITEMS = []
    yield items
    await cleanup_helper(client, items)


"""Helper method to create and verify dataset"""

async def create_and_verify_dataset(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> str:
    created_organisation = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)
    assert created_organisation, "The organisation failed to create."
    assert created_organisation.created_item, "Created organisation does not contain a created item response"
    assert created_organisation.created_item.id, "Created organisation does not contain a handle ID."
    cleanup_items.append((ItemSubType.ORGANISATION, created_organisation.created_item.id))

    created_person = await create_item(client=client, item_subtype=ItemSubType.PERSON)
    assert created_person, "The person failed to create."
    assert created_person.created_item, "Created person does not contain a created item response"
    assert created_person.created_item.id, "Created person does not contain a handle ID"
    cleanup_items.append((ItemSubType.PERSON, created_person.created_item.id))

    dataset_domain_info = get_item_subtype_domain_info_example(ItemSubType.DATASET)
    dataset_domain_info = cast(DatasetDomainInfo, dataset_domain_info)
    dataset_domain_info = dataset_domain_info.collection_format

    # Override the dataset domain info example object with newly created organisations and persons
    dataset_domain_info.associations.organisation_id = created_organisation.created_item.id
    dataset_domain_info.associations.data_custodian_id = created_person.created_item.id
    dataset_domain_info.dataset_info.publisher_id = created_organisation.created_item.id

    mint_response = await client.datastore.mint_dataset(dataset_mint_info=dataset_domain_info)
    assert mint_response.status.success, "Reported failure when minting dataset"
    assert mint_response.handle, "Mint response does not contain a handle"
    cleanup_items.append((ItemSubType.DATASET, mint_response.handle))

    # Fetch dataset by created handle_id
    dataset_fetch_response = await client.datastore.fetch_dataset(mint_response.handle)
    dataset_fetch_item = dataset_fetch_response.item
    assert dataset_fetch_response.status.success, f"Reported failure when fetching dataset with id {mint_response.handle}"
    assert dataset_fetch_item is not None, "Fetched Dataset is null/none"
    assert dataset_fetch_item.id == mint_response.handle

    # Ensure the workflow links were updated
    assert dataset_fetch_item.workflow_links
    assert dataset_fetch_item.workflow_links.create_activity_workflow_id

    assert mint_response.register_create_activity_session_id

    create_activity_response = await client.job_api.await_successful_job_completion(
        session_id=mint_response.register_create_activity_session_id
    )
    assert create_activity_response.result is not None
    parsed_result = RegistryRegisterCreateActivityResult.parse_obj(
        create_activity_response.result)

    lodge_session_id = parsed_result.lodge_session_id
    creation_activity_id = parsed_result.creation_activity_id

    # Clean up dataset Create side effect
    cleanup_items.append((ItemSubType.CREATE, creation_activity_id))

    # Wait for next step of lifecycle - step 2
    await client.job_api.await_successful_job_completion(session_id=lodge_session_id)

    # Check the Create activity was produced and is accurate
    fetched_create_activity_response = await client.registry.create_activity.fetch(id=creation_activity_id)
    assert fetched_create_activity_response.item
    assert fetched_create_activity_response.item.id == creation_activity_id

    return mint_response.handle

async def health_check_of_all_apis(client: ProvenaClient) -> None:

    health_check_successful_message = "Health check successful."

    auth_api = await client.auth_api.get_health_check()
    assert auth_api.message  == health_check_successful_message

    datastore = await client.datastore.get_health_check()
    assert datastore.message == health_check_successful_message

    prov = await client.prov_api.get_health_check()
    assert prov.message == health_check_successful_message

    registry = await client.registry.get_health_check()
    assert registry.message == health_check_successful_message

    job_api = await client.job_api.get_health_check()
    assert job_api.message == health_check_successful_message


"""Datastore"""

@pytest.mark.asyncio
async def test_invalid_handle_fetch_dataset(client: ProvenaClient) -> None:

    invalid_dataset_handle = "1234567890123"

    with pytest.raises(BadRequestException):
        await client.datastore.fetch_dataset(id = invalid_dataset_handle)

@pytest.mark.asyncio
async def test_register_dataset(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:
    
    dataset_handle = await create_and_verify_dataset(client, cleanup_items)
    assert dataset_handle, "Dataset handle should not be None or empty."
    
"""Search-API related tests and finding newly related items."""

@pytest.mark.asyncio
async def test_searching_dataset(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:

    dataset_handle = await create_and_verify_dataset(client, cleanup_items)
    assert dataset_handle, "Dataset handle should not be None or empty."

    # Perform search using the dataset handles
    search_response = await client.search.search_registry(query=dataset_handle, subtype_filter=ItemSubType.DATASET, limit = None)
    assert search_response.status.success, f"Search failed for dataset with handle {dataset_handle}"
    assert search_response.results, "No results obtained from search!"
    search_result_ids = [result.id for result in search_response.results]
    assert dataset_handle in search_result_ids, f"{dataset_handle} not found in search results"

@pytest.mark.asyncio
async def test_search_non_chained_entites(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:

    # Organisations 
    organisation_domain_info = get_item_subtype_domain_info_example(ItemSubType.ORGANISATION)
    orgainsation_domain_info = cast(OrganisationDomainInfo, organisation_domain_info)

    created_org = await client.registry.organisation.create_item(create_item_request=orgainsation_domain_info)
    assert created_org.status.success, "Reported failure when creating organisation"
    assert created_org.created_item, "Created organisation does not contain a created item response"
    assert created_org.created_item.id, "Created organisation does not contain an handle ID"

    created_org_id = created_org.created_item.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id))
    time.sleep(5)

    search_response = await client.search.search_registry(query=created_org_id, subtype_filter=ItemSubType.ORGANISATION, limit = None)
    assert search_response.status.success, f"Search failed for organisation with  handle {created_org_id}"
    assert search_response.results
    search_result_ids = [result.id for result in search_response.results]
    assert created_org_id in search_result_ids, f"{created_org_id} not found in search results"

    # Person
    person_domain_info = get_item_subtype_domain_info_example(ItemSubType.PERSON)
    person_domain_info = cast(PersonDomainInfo, person_domain_info)

    created_person = await client.registry.person.create_item(create_item_request=person_domain_info)
    assert created_person.status.success, "Reported failure when creating person"
    assert created_person.created_item, "Created person does not contain a created item response"
    assert created_person.created_item.id, "Created person does not contain an handle ID"

    person_id = created_person.created_item.id
    cleanup_items.append((ItemSubType.PERSON, created_person.created_item.id))
    time.sleep(5)

    search_response = await client.search.search_registry(query=person_id, subtype_filter=ItemSubType.PERSON, limit = None)
    assert search_response.status.success, f"Search failed for person with handle {person_id}"
    assert search_response.results
    search_result_ids = [result.id for result in search_response.results]
    assert person_id in search_result_ids, f"{person_id} not found in search results"

    # Study
    study_domain_info = get_item_subtype_domain_info_example(ItemSubType.STUDY)
    study_domain_info = cast(StudyDomainInfo, study_domain_info)

    created_study = await client.registry.study.create_item(create_item_request=study_domain_info)
    assert created_study.status.success, "Reported failure when creating study entity"
    assert created_study.created_item, "Created study entity does not contain a created item response"
    assert created_study.created_item.id, "Created study entity does not contain an handle ID"

    study_id = created_study.created_item.id
    cleanup_items.append((ItemSubType.STUDY, created_study.created_item.id))
    time.sleep(5)

    search_response = await client.search.search_registry(query=study_id, subtype_filter=ItemSubType.STUDY, limit = None)
    assert search_response.status.success, f"Search failed for study with handle {study_id}"
    assert search_response.results
    search_result_ids = [result.id for result in search_response.results]
    assert study_id in search_result_ids, f"{study_id} not found in search results"

    # Models 

    model_domain_info = get_item_subtype_domain_info_example(ItemSubType.MODEL)
    model_domain_info = cast(ModelDomainInfo, model_domain_info)

    created_model = await client.registry.model.create_item(create_item_request=model_domain_info)
    assert created_model.status.success, "Reported failure when creating models"
    assert created_model.created_item, "Created model does not contain a created item response"
    assert created_model.created_item.id, "Created model does not contain an handle ID"

    created_model_id = created_model.created_item.id
    cleanup_items.append((ItemSubType.MODEL,created_model_id))
    time.sleep(5)

    search_response = await client.search.search_registry(query=created_model_id, subtype_filter=ItemSubType.MODEL, limit = None)
    assert search_response.status.success, f"Search failed for model with handle {created_model_id}"
    assert search_response.results
    search_result_ids = [result.id for result in search_response.results]
    assert created_model_id in search_result_ids, f"{created_model_id} not found in search results"



"""Listing items that is present. - No Pagination"""

@pytest.mark.asyncio
async def test_list_all_datasets(client: ProvenaClient) -> None: 

    datasets = await client.datastore.list_all_datasets()
    assert datasets is not None
    assert len(datasets) > 0

@pytest.mark.asyncio
async def test_export_all_items_in_registry(client: ProvenaClient) -> None:

    all_items_in_registry = await client.registry.admin.export_items()
    assert all_items_in_registry is not None, "Failed to export all items from the registry"
    assert all_items_in_registry.status.success, "Failed to export all items from registry."
    assert all_items_in_registry.items, "Failed to find 'items' within registry export"
    assert len(all_items_in_registry.items) > 0, "Registry export failed. Item count is >= 1"

"""Listing Datastore Items and Registry Items - Pagination Present"""

@pytest.mark.asyncio
async def test_datastore_pagination(client: ProvenaClient) -> None:

    """Testing generally"""
    list_dataset_request = NoFilterSubtypeListRequest(
            sort_by=None, 
            pagination_key=None
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request)

    assert dataset_list, f"Datastore dataset list is None or Null."
    assert dataset_list.status.success, f"Datastore dataset fetch failed with status {dataset_list.status.details}"
    assert dataset_list.items, f"Dataset list does not contain items field."

    """Testing with different sort criteria"""

    list_dataset_request = NoFilterSubtypeListRequest(
            sort_by=SortOptions(sort_type=SortType.DISPLAY_NAME, ascending=True, begins_with=None), 
            pagination_key=None
        )
    
    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request)
    assert dataset_list, f"Datastore dataset list is None or Null."
    assert dataset_list.status.success, f"Datastore dataset fetch failed with status {dataset_list.status.details}"
    assert dataset_list.items, f"Dataset list does not contain items field."
    sorted_names = [item.display_name for item in dataset_list.items]
    assert sorted_names == sorted(sorted_names), "Datasets are not sorted by DISPLAY_NAME in ascending order"

    list_dataset_request_two = NoFilterSubtypeListRequest(
        sort_by=SortOptions(sort_type=SortType.CREATED_TIME, ascending=True, begins_with=None),
        pagination_key=None
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request_two)
    assert dataset_list, f"Datastore dataset list is None or Null."
    assert dataset_list.status.success, f"Datastore dataset fetch failed with status {dataset_list.status.details}"
    assert dataset_list.items, f"Dataset list does not contain items field."
    sorted_dates = [(item.collection_format.dataset_info.created_date) for item in dataset_list.items]
    assert sorted_dates == sorted(sorted_dates), "Datasets are not sorted by CREATED_TIME in ascending order"

    """Testing with different page sizes"""

    list_dataset_request_three = NoFilterSubtypeListRequest(
        sort_by=None, 
        pagination_key=None, 
        page_size=2
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request_three)
    assert dataset_list, f"Datastore dataset list is None or Null."
    assert dataset_list.status.success, f"Datastore dataset fetch failed with status {dataset_list.status.details}"
    assert dataset_list.items, f"Dataset list does not contain items field."
    assert len(dataset_list.items) == 2, f"Dataset list exceed page size. Something is wrong!"


"""Provenance"""

@pytest.mark.asyncio
async def test_search_other_items(client: ProvenaClient, cleanup_items: List[Tuple[ItemSubType, IdentifiedResource]]) -> None:

    # Model Run Workflow Template
    mrwt_domain_info = get_item_subtype_domain_info_example(ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE)
    mwrt_domain_info = cast(ModelRunWorkflowTemplateDomainInfo, mrwt_domain_info)

    created_template = await client.registry.model_run_workflow.create_item(create_item_request=mwrt_domain_info)
    assert created_template.status.success, "Reported failure when creating model run workflow template"
    assert created_template.created_item, "Created workflow template does not contain a created item response"
    assert created_template.created_item.id

    template_id = created_template.created_item.id
    cleanup_items.append((ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE, template_id))

    search_response = await client.search.search_registry(query=template_id, subtype_filter=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE, limit = None)
    assert search_response.status.success, f"Search failed for model run workflow template with handle {template_id}"
    assert search_response.results
    assert template_id in search_response.results

    

"""Querying Provenance"""





