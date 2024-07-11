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
from ProvenaInterfaces.ProvenanceModels import *

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



"""Listing items that is present. - No Pagination Testing"""

@pytest.mark.asyncio
async def test_list_all_datasets(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None: 

    """Create dataset"""
    dataset_handle = await create_and_verify_dataset(client=client, cleanup_items=cleanup_items)

    """Fetch all datasets, and test if the datasets we created are part of this list."""

    datasets = await client.datastore.list_all_datasets()
    assert datasets is not None, "Datastore dataset list is None or Null."
    assert len(datasets) > 0, "Datastore dataset list is empty"

    # Get handles of datasets from datastore.
    returned_dataset_ids = {dataset.id for dataset in datasets}
    
    # Check if all test dataset IDs are in the returned dataset IDs
    assert dataset_handle in returned_dataset_ids, f"Test dataset with ID {dataset_handle} not in the datastore."

@pytest.mark.asyncio
async def test_list_registry_items(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:

    """Fetches items from registry based on their subtype, and asserts that the created items
    during the integration tests are present."""

    generic_list_request = GeneralListRequest(
        filter_by=None,
        sort_by=None,
        pagination_key=None, 
        page_size=100
    )

   # Organisations
    created_organisation = await create_item(client = client, item_subtype = ItemSubType.ORGANISATION)
    assert created_organisation is not None, "Created organisation is Null or None"
    assert created_organisation.created_item is not None, "Created organisation is missing field created_item"
    assert created_organisation.created_item.id is not None, "Created organisation is missing handle ID"
    created_org_id = created_organisation.created_item.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id))


    organisation_list = await client.registry.organisation.list_items(list_items_payload=generic_list_request)
    assert organisation_list is not None, "Organisation List is None or Null"
    assert organisation_list.items, "Organisation list items field not present."
    # Get all handles of Organisations from org_list 
    returned_organisation_ids = {org.id for org in organisation_list.items} 
    assert created_organisation.created_item.id in returned_organisation_ids, f"Organisation with ID {created_organisation.created_item.id} not in registry."

    # Person
    created_person = await create_item(client=client, item_subtype=ItemSubType.PERSON)
    assert created_person is not None, "Created person is Null or None"
    assert created_person.created_item is not None, "Created person is missing field created_item"
    assert created_person.created_item.id is not None, "Created person is missing handle ID"
    created_person_id = created_person.created_item.id
    cleanup_items.append((ItemSubType.PERSON, created_person_id))

    person_list = await client.registry.person.list_items(list_items_payload=generic_list_request)
    assert person_list is not None, "Person List is None or Null"
    assert person_list.items, "Person list items field not present."
    returned_person_ids = {person.id for person in person_list.items}
    assert created_person.created_item.id in returned_person_ids, f"Person with ID {created_person.created_item.id} not in registry."

    # Study
    created_study = await create_item(client=client, item_subtype=ItemSubType.STUDY)
    assert created_study is not None, "Created study is Null or None"
    assert created_study.created_item is not None, "Created study is missing field created_item"
    assert created_study.created_item.id is not None, "Created study is missing handle ID"
    created_study_id = created_study.created_item.id
    cleanup_items.append((ItemSubType.STUDY, created_study_id))

    study_list = await client.registry.study.list_items(list_items_payload=generic_list_request)
    assert study_list is not None, "Study List is None or Null"
    assert study_list.items, "Study list items field not present."
    returned_study_ids = {study.id for study in study_list.items}
    assert created_study.created_item.id in returned_study_ids, f"Study with ID {created_study.created_item.id} not in registry."

    # Models
    created_model = await create_item(client=client, item_subtype=ItemSubType.MODEL)
    assert created_model is not None, "Created model is Null or None"
    assert created_model.created_item is not None, "Created model is missing field created_item"
    assert created_model.created_item.id is not None, "Created model is missing handle ID"
    created_model_id = created_model.created_item.id
    cleanup_items.append((ItemSubType.MODEL, created_model_id))

    model_list = await client.registry.model.list_items(list_items_payload=generic_list_request)
    assert model_list is not None, "Model List is None or Null"
    assert model_list.items, "Model list items field not present."
    returned_model_ids = {model.id for model in model_list.items}
    assert created_model.created_item.id in returned_model_ids, f"Model with ID {created_model.created_item.id} not in registry."


@pytest.mark.asyncio
async def test_export_all_items_in_registry(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:

    created_organisation = await create_item(client = client, item_subtype = ItemSubType.ORGANISATION)
    assert created_organisation is not None, "Created organisation is Null or None"
    assert created_organisation.created_item is not None, "Created organisation is missing field created_item"
    assert created_organisation.created_item.id is not None, "Created organisation is missing handle ID"
    created_org_id = created_organisation.created_item.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id))

    all_items_in_registry = await client.registry.admin.export_items()
    assert all_items_in_registry is not None, "Failed to export all items from the registry"
    assert all_items_in_registry.status.success, "Failed to export all items from registry."
    assert all_items_in_registry.items, "Failed to find 'items' within registry export"
    assert len(all_items_in_registry.items) > 0, "Registry export failed. Item count is >= 1"


"""Listing Datastore Items and Registry Items - Pagination Present"""

@pytest.mark.asyncio
async def test_datastore_pagination(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:

    dataset_handle_1 = await create_and_verify_dataset(client = client, cleanup_items = cleanup_items)
    dataset_handle_2 = await create_and_verify_dataset(client = client, cleanup_items = cleanup_items)
    
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
    sorted_dates = [(item.created_timestamp) for item in dataset_list.items]
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


@pytest.mark.asyncio
async def test_registry_pagination(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:

    created_organisation_1 = await create_item(client = client, item_subtype = ItemSubType.ORGANISATION)
    assert created_organisation_1 is not None, "Created organisation is Null or None"
    assert created_organisation_1.created_item is not None, "Created organisation is missing field created_item"
    assert created_organisation_1.created_item.id is not None, "Created organisation is missing handle ID"
    created_org_id_1 = created_organisation_1.created_item.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id_1))

    created_organisation_2 = await create_item(client = client, item_subtype = ItemSubType.ORGANISATION)
    assert created_organisation_2 is not None, "Created organisation is Null or None"
    assert created_organisation_2.created_item is not None, "Created organisation is missing field created_item"
    assert created_organisation_2.created_item.id is not None, "Created organisation is missing handle ID"
    created_org_id_2 = created_organisation_2.created_item.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id_2))

    sort_request = GeneralListRequest(
        filter_by=None,
        sort_by=SortOptions(sort_type=SortType.DISPLAY_NAME, ascending=True, begins_with=None),
        pagination_key=None,
        page_size=100
    )
    
    sorted_organisation_list = await client.registry.organisation.list_items(list_items_payload=sort_request)
    assert sorted_organisation_list, "Sorted Organisation List is None or Null"
    assert sorted_organisation_list.items, "Sorted organisation list items field not present."
    sorted_names = [item.display_name for item in sorted_organisation_list.items]
    assert sorted_names == sorted(sorted_names), "Organisations are not sorted by DISPLAY_NAME in ascending order"

    sort_request.sort_by = SortOptions(sort_type=SortType.CREATED_TIME, ascending=True, begins_with=None)

    sorted_organisation_list = await client.registry.organisation.list_items(list_items_payload=sort_request)
    assert sorted_organisation_list, "Sorted Organisation List is None or Null"
    assert sorted_organisation_list.items, "Sorted organisation list items field not present."
    sorted_dates = [item.created_timestamp for item in sorted_organisation_list.items]
    assert sorted_dates == sorted(sorted_dates), "Organisations are not sorted by CREATED_TIME in ascending order"

    # Testing with different page sizes for organisations
    page_request = GeneralListRequest(
        filter_by=None,
        sort_by=None, 
        pagination_key=None, 
        page_size=2
    )

    paged_organisation_list = await client.registry.organisation.list_items(list_items_payload=page_request)
    assert paged_organisation_list, "Paged Organisation List is None or Null"
    assert paged_organisation_list.items, "Paged organisation list items field not present."
    assert len(paged_organisation_list.items) == 2, "Paged organisation list exceeds page size. Something is wrong!"

"""Provenance - Registring Model Runs Etc.."""

async def test_provenance_workflow(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:
    # prov test that will create the requirements needed for a model run record and register it
    # Procedure:
    # create the simple entities required (person, organisation)
    # register custom dataset templates for input and output datasets
    # register simple model
    # register model run workflow tempalte using references to pre registered entities
    # create and register the model run object using references to pre registered entitites

    # Create datasets needed for model runs
    dataset_1_id = await create_and_verify_dataset(client = client, cleanup_items=cleanup_items)
    dataset_2_id = await create_and_verify_dataset(client = client, cleanup_items=cleanup_items)

    person = await create_item(client = client, item_subtype = ItemSubType.PERSON)
    assert person is not None, "Created person is None"
    assert person.created_item is not None, "Created person does not contain created_item"
    assert person.created_item.id is not None, "Created person does not have handle ID"

    organisation = await create_item(client = client, item_subtype = ItemSubType.ORGANISATION)
    assert organisation is not None, "Created organisation is None"
    assert organisation.created_item is not None, "Created organisation does not contain created_item"
    assert organisation.created_item.id is not None, "Created organisation does not have handle ID"


    # register custom dataset templates (input and output)
    input_template = await create_item(client = client, item_subtype= ItemSubType.DATASET_TEMPLATE)
    assert input_template is not None, "Created input template is None"
    assert input_template.created_item is not None, "Created input template does not contain created_item"
    assert input_template.created_item.id is not None, "Created input template does not have handle ID"

    cleanup_items.append((ItemSubType.DATASET_TEMPLATE, input_template.created_item.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client = client,
        item=input_template.created_item,
        cleanup_items=cleanup_items
    )

    output_template = await create_item(client = client, item_subtype= ItemSubType.DATASET_TEMPLATE)
    assert output_template is not None, "Created ouput template is None"
    assert output_template.created_item is not None, "Created ouput template does not contain created_item"
    assert output_template.created_item.id is not None, "Created ouput template does not have handle ID"

    cleanup_items.append((ItemSubType.DATASET_TEMPLATE, output_template.created_item.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client = client,
        item=output_template.created_item,
        cleanup_items=cleanup_items
    )

    # Register the model used in the model run
    model = await create_item(client = client, item_subtype= ItemSubType.MODEL)
    assert model is not None, "Created model is None"
    assert model.created_item is not None, "Created model does not contain created_item"
    assert model.created_item.id is not None, "Created model does not have handle ID"

    cleanup_items.append((ItemSubType.MODEL, model.created_item.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client = client,
        item=model.created_item,
        cleanup_items=cleanup_items
    )

    # create and register model run workflow template
    required_annotation_key = "annotation_key1"
    optional_annotation_key = "annotation_key2"
    mrwt_domain_info = ModelRunWorkflowTemplateDomainInfo(
        display_name="IntegrationTestMRWT",
        software_id=model.created_item.id,  # model is software
        input_templates=[TemplateResource(
            template_id=input_template.created_item.id, optional=False)],
        output_templates=[TemplateResource(
            template_id=output_template.created_item.id, optional=False)],
        annotations=WorkflowTemplateAnnotations(
            required=[required_annotation_key],
            optional=[optional_annotation_key]
        ), 
        user_metadata=None
    )
    mrwt = await create_item_from_domain_info_successfully(
        client = client,
        item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
        domain_info=mrwt_domain_info)
    assert mrwt is not None, "Created Model Run Workflow Template is None"
    assert mrwt.created_item is not None, "Created Model Run Workflow Template does not contain created_item"
    assert mrwt.created_item.id is not None, "Created Model Run Workflow Template does not have handle ID"

    cleanup_items.append((ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE, mrwt.created_item.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client = client,
        item=mrwt.created_item,
        cleanup_items=cleanup_items
    )

    # create model run to register
    model_run_record = ModelRunRecord(
        workflow_template_id=mrwt.created_item.id,
        inputs=[TemplatedDataset(
            dataset_template_id=input_template.created_item.id,
            dataset_id=dataset_1_id,
            dataset_type=DatasetType.DATA_STORE,
            resources={
                "input_deferred_resource_key": "/path/to/resource.csv"
            }
        )],
        outputs=[TemplatedDataset(
            dataset_template_id=output_template.created_item.id,
            dataset_id=dataset_2_id,
            dataset_type=DatasetType.DATA_STORE,
            resources={
                "output_deferred_resource_key": "/path/to/resource.csv"
            }
        )],
        associations=AssociationInfo(
            modeller_id=person.created_item.id,
            requesting_organisation_id=organisation.created_item.id
        ),
        display_name="Integration test fake model run display name",
        start_time=int((datetime.now().timestamp())),
        end_time=int((datetime.now().timestamp())),
        description="Integration test fake model run",
        annotations={
            required_annotation_key: 'somevalue',
            optional_annotation_key: 'some other optional value'
        }
    )

    # register model run
    response_model_run_record = await register_model_run_successfully(
        client = client, 
        model_run_record= model_run_record
    )

    model_run_id = response_model_run_record.id
    cleanup_items.append((ItemSubType.MODEL_RUN, model_run_id))

    # create model run to register including a linked study
    study = await create_item(
        client = client,
        item_subtype=ItemSubType.STUDY)
    
    assert study is not None, "Created study is None"
    assert study.created_item is not None, "Created study does not contain created_item"
    assert study.created_item.id is not None, "Created study does not have handle ID"
    
    cleanup_items.append((ItemSubType.STUDY, study.created_item.id))

    model_run_record.study_id = study.created_item.id

    # register model run
    response_model_run_record = await register_model_run_successfully(
        client = client, 
        model_run_record = model_run_record
    )

    model_run_id = response_model_run_record.id
    cleanup_items.append((ItemSubType.MODEL_RUN, model_run_id))

    # - check the prov graph lineage is appropriate

    # The lineage should have 
    
    activity_upstream_query = await client.prov_api.explore_upstream(
        starting_id=model_run_id,
        depth=1,
    )

    # model run -wasInformedBy-> study
    assert_non_empty_graph_property(
        prop=GraphProperty(
            type="wasInformedBy",
            source=model_run_id,
            target=study.created_item.id
        ),
        lineage_response=activity_upstream_query
    )


    # ensure invalid study id results in failure
    model_run_record.study_id = '1234'

    # register model run
    failed, possible_model_run_record = register_modelrun_from_record_info_failed(
        get_token=write_token, model_run_record=model_run_record, expected_code=400)

    if not failed:
        assert possible_model_run_record
        model_run_id = possible_model_run_record.id
        cleanup_items.append((ItemSubType.MODEL_RUN, model_run_id))
        assert False, f"Model run registration with invalid study should have failed, but did not."



"""Querying Provenance"""






