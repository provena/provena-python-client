'''
Created Date: Wednesday June 26th 2024 +0000
Author: Parth Kuulkarni
-----
Last Modified: Wednesday June 26th 2024 3:16:19 PM +0000
Modified By: Parth Kulkarni
-----
Description: Integration tests for the client library!
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------

01-08-2024 | Parth Kulkarni | Updated Integration Tests based on PR feedback. Needs further review. 
11-07-2024 | Parth Kulkarni | Completed Integration Testing (Need Review) 
10-07-2024 | Parth Kulkarni | In Progress of Integration Testing. 

'''

from pathlib import Path
import shutil
from typing import Any, AsyncGenerator, List, cast
import pytest
import pytest_asyncio

from provenaclient.auth import DeviceFlow, OfflineFlow
from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.utils.config import Config

from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.AsyncJobModels import RegistryRegisterCreateActivityResult
from ProvenaInterfaces.ProvenanceModels import *
from ProvenaInterfaces.AuthAPI import UserLinkUserAssignRequest
from dotenv import load_dotenv

from integration_helpers import *
from provenaclient.utils.exceptions import BadRequestException
import time
import os



@pytest.fixture(scope="session")
def auth_manager() -> OfflineFlow:

    load_dotenv()
    domain = os.getenv("DOMAIN")
    realm_name = os.getenv("REALM_NAME")
    offline_token = os.getenv("PROVENA_ADMIN_OFFLINE_TOKEN")
    client_id = os.getenv("CLIENT_ID")

    assert domain, "DOMAIN environment variable is not set"
    assert realm_name, "REALM_NAME environment variable is not set"
    assert offline_token, "PROVENA_ADMIN_OFFLINE_TOKEN environment variable is not set"
    assert client_id, "CLIENT_ID environment variable is not set"

    config = Config(
        domain=domain,
        realm_name=realm_name
    )

    return OfflineFlow(config=config, client_id=client_id, offline_token=offline_token, offline_token_file=None)


@pytest.fixture(scope="session")
def client(auth_manager: OfflineFlow) -> ProvenaClient:
    """Insinatates the Provena Client"""

    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    return ProvenaClient(config=config, auth=auth_manager)


@pytest_asyncio.fixture(scope="session")
async def org_person_fixture(client: ProvenaClient) -> AsyncGenerator[Tuple[ItemBase, ItemBase], None]:
    """ A fixture to generate organisation and person entities.
    """
    created_organisation = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)

    # create a person and link it to me (the user of the client)
    # because I require to be linked to create datasets in later tests
    created_person = await create_item(client=client, item_subtype=ItemSubType.PERSON)

    # check if somehow already linked to ID (test fail also failed cleanup), if so clear associated links
    user_link_lookup_resp = await client.auth_api.get_link_lookup_username()
    if user_link_lookup_resp.person_id is not None:
        # clear all links associated with this person ID (potentially my many accounts)
        await clear_all_links_with_person_id_user(
            client=client, person_id=user_link_lookup_resp.person_id)
    else:
        # fresh slate, now assign so theres only one link
        await client.auth_api.post_link_assign(body=UserLinkUserAssignRequest(person_id=created_person.id))

    # Provide the Org and Person to each test that requires it.
    yield created_organisation, created_person

    # link clean up before item is deleted as we use ID to find the username(s) to remove the link
    await clear_all_links_with_person_id_user(client=client, person_id=created_person.id)

    # now remove the entities
    await cleanup_helper(client=client,
                         list_of_handles=[(created_organisation.item_subtype, created_organisation.id),
                                          (created_person.item_subtype,
                                           created_person.id)
                                          ])


@pytest_asyncio.fixture(scope="session")
async def dataset_fixture(client: ProvenaClient, org_person_fixture: Tuple[ItemBase, ItemBase], cleanup_items: CLEANUP_ITEMS) -> AsyncGenerator[Tuple[str, str], None]:
    """A fixture that creates two datasets at the start of the testing cycle. This is done 
       at the start for optimisation purposes and reduce overall testing time.

       This assures that at minimum there is always two datasets present.

    Parameters
    ----------
    client : ProvenaClient
        Provena client tooling.

    Returns
    -------
    AsyncGenerator[CollectionFormat, None]
        _description_
    """

    created_dataset_1: str = await create_and_verify_dataset(client=client, org_person_fixture=org_person_fixture, cleanup_items=cleanup_items)
    created_dataset_2: str = await create_and_verify_dataset(client=client, org_person_fixture=org_person_fixture, cleanup_items=cleanup_items)

    yield created_dataset_1, created_dataset_2


@pytest_asyncio.fixture(scope="session")
async def cleanup_items(client: ProvenaClient) -> AsyncGenerator[CLEANUP_ITEMS, None]:
    """ Stores all entites minted as a part of the integration test for cleanup purposes."""

    items: CLEANUP_ITEMS = []
    yield items
    await cleanup_helper(client, items)


async def create_and_verify_dataset(client: ProvenaClient, org_person_fixture: Tuple[ItemBase, ItemBase], cleanup_items: CLEANUP_ITEMS) -> str:
    """Helper method to create datasets and related chained entities needed."""

    created_organisation, created_person = org_person_fixture

    dataset_domain_info = get_item_subtype_domain_info_example(
        ItemSubType.DATASET)
    dataset_domain_info = cast(DatasetDomainInfo, dataset_domain_info)
    dataset_domain_info = dataset_domain_info.collection_format

    # Override the dataset domain info example object with newly created organisations and persons
    dataset_domain_info.associations.organisation_id = created_organisation.id
    dataset_domain_info.associations.data_custodian_id = created_person.id
    dataset_domain_info.dataset_info.publisher_id = created_organisation.id

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


@pytest.mark.asyncio
async def test_health_check_of_all_apis(client: ProvenaClient) -> None:
    """Health checks all API's"""

    health_check_successful_message = "Health check successful."

    auth_api = await client.auth_api.get_health_check()
    assert auth_api.message == health_check_successful_message

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
    """Attempts to fetch invalid dataset handle"""

    invalid_dataset_handle = "1234567890123"

    with pytest.raises(BadRequestException):
        await client.datastore.fetch_dataset(id=invalid_dataset_handle)


@pytest.mark.asyncio
async def test_register_dataset(client: ProvenaClient, org_person_fixture: Tuple[ItemBase, ItemBase], cleanup_items: CLEANUP_ITEMS) -> None:
    """Register dataset through helper function."""

    dataset_handle = await create_and_verify_dataset(client, org_person_fixture, cleanup_items)
    assert dataset_handle, "Dataset handle should not be None or empty."

@pytest.mark.asyncio
async def test_specific_file_directory_download_from_dataset(client: ProvenaClient, dataset_fixture: Tuple[str, str]) -> None:
    """Datastore I/O Functionality Testing"""

    # Ignoring the second dataset (Only testing on one)
    created_dataset_1_handle, _ = dataset_fixture

    # Set out the paths for the source and destination directories
    source_directory = Path("./test_source_directory")
    destination_directory = Path("./test_destination_directory")
    test_file_name = "test.txt"

    try:
        # Create the source directory
        source_directory.mkdir(parents=True, exist_ok=True)

        # Assert that the source directory does exist 
        assert source_directory.exists(), f"Missing the source directory {source_directory} cannot proceed further."        

        # Generate random file within the directory
        file_name_1 = source_directory / test_file_name
        file_name_1.write_text("testing integration test")

        # Upload everything in the source directory
        await client.datastore.io.upload_all_files(
            source_directory=str(source_directory),
            dataset_id=created_dataset_1_handle
        )

        # Create the destination directory
        destination_directory.mkdir(parents=True, exist_ok=True)

        # Now downloading specific file to see if everything is available
        await client.datastore.io.download_specific_file(
            dataset_id=created_dataset_1_handle,
            s3_path=test_file_name,
            destination_directory=str(destination_directory)
        )

        # Assert that the file is present within the destination/custom directory.
        downloaded_file_path = destination_directory / test_file_name
        assert downloaded_file_path.exists(), f"File was not downloaded correctly to {downloaded_file_path}"

        # Assert that the destination/custom directory does exist 
        assert destination_directory.exists(), f"Missing the custom/destination directory {destination_directory}"        

    finally:
        if source_directory.exists():
            shutil.rmtree(source_directory)
        if destination_directory.exists():
            shutil.rmtree(destination_directory)

"""Search-API related tests and finding newly related items."""
@pytest.mark.asyncio
async def test_searching_dataset(client: ProvenaClient, dataset_fixture: Tuple[str, str], cleanup_items: CLEANUP_ITEMS) -> None:
    """Searches for dataset that were created start of the test."""

    created_dataset_1_handle, created_dataset_2_handle = dataset_fixture

    assert created_dataset_1_handle, "Dataset handle should not be None or empty."
    assert created_dataset_2_handle, "Dataset handle should not be None or empty."

    # Perform search using the dataset handles
    time.sleep(10)  # give search api time to detect and index
    await search_and_assert(client=client, item_id=created_dataset_1_handle, item_subtype=ItemSubType.DATASET, sleep_time=0)
    await search_and_assert(client=client, item_id=created_dataset_2_handle, item_subtype=ItemSubType.DATASET, sleep_time=0)


@pytest.mark.asyncio
async def test_search_created_entites(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:
    """Searches all registry items, by first creating them and then uses search api to search. """

    # Create an organisation and asserts/validates inside create_item
    organisation = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)

    # Explicitly assert the creation for clarity
    assert organisation is not None, "Failed to create organisation"
    assert organisation.id is not None, "Created organisation does not have an ID"
    cleanup_items.append((ItemSubType.PERSON, organisation.id))

    # Person
    person = await create_item(client=client, item_subtype=ItemSubType.PERSON)
    assert person is not None, "Failed to create person"
    assert person.id is not None, "Created person does not have an ID"
    cleanup_items.append((ItemSubType.PERSON, person.id))

    # Study
    study = await create_item(client=client, item_subtype=ItemSubType.STUDY)
    assert study is not None, "Failed to create study"
    assert study.id is not None, "Created study does not have an ID"
    cleanup_items.append((ItemSubType.STUDY, study.id))

    # Model
    model = await create_item(client=client, item_subtype=ItemSubType.MODEL)
    assert model is not None, "Failed to create model"
    assert model.id is not None, "Created model does not have an ID"
    cleanup_items.append((ItemSubType.MODEL, model.id))

    time.sleep(10)  # give search api time to detect and index
    await search_and_assert(client=client, item_id=organisation.id, item_subtype=ItemSubType.ORGANISATION, sleep_time=0)
    await search_and_assert(client=client, item_id=person.id, item_subtype=ItemSubType.PERSON, sleep_time=0)
    await search_and_assert(client=client, item_id=study.id, item_subtype=ItemSubType.STUDY, sleep_time=0)
    await search_and_assert(client=client, item_id=model.id, item_subtype=ItemSubType.MODEL, sleep_time=0)


"""Listing items that is present. - No Pagination Testing"""


@pytest.mark.asyncio
async def test_list_all_datasets(client: ProvenaClient, dataset_fixture: Tuple[str, str], cleanup_items: CLEANUP_ITEMS) -> None:
    """Retrieves datastore dataset list and assert that
       recently created dataset is present."""

    # Grab handles of dataset created start of the test.
    dataset_1_handle, dataset_2_handle = dataset_fixture

    # Fetch all datasets, and test if the datasets we created are part of this list.
    datasets = await client.datastore.list_all_datasets()
    assert datasets is not None, "Datastore dataset list is None or Null."
    assert len(datasets) > 0, "Datastore dataset list is empty"

    # Get handles of datasets from datastore.
    returned_dataset_ids = {dataset.id for dataset in datasets}

    # Check if all test dataset IDs are in the returned dataset IDs
    assert dataset_1_handle in returned_dataset_ids, f"Test dataset with ID {dataset_1_handle} not in the datastore."
    assert dataset_2_handle in returned_dataset_ids, f"Test dataset with ID {dataset_2_handle} not in the datastore."


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
    created_organisation = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)
    created_org_id = created_organisation.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id))

    organisation_list = await client.registry.organisation.list_items(list_items_payload=generic_list_request)
    organisation_list_items: List[ItemOrganisation] = assert_list_items(
        item=organisation_list, item_subtype=ItemSubType.ORGANISATION)
    # Get all handles of Organisations from org_list
    returned_organisation_ids = {org.id for org in organisation_list_items}
    assert created_org_id in returned_organisation_ids, f"Organisation with ID {created_org_id} not in registry."

    # Person
    created_person = await create_item(client=client, item_subtype=ItemSubType.PERSON)
    created_person_id = created_person.id
    cleanup_items.append((ItemSubType.PERSON, created_person_id))

    person_list = await client.registry.person.list_items(list_items_payload=generic_list_request)
    person_list_items: List[ItemPerson] = assert_list_items(
        item=person_list, item_subtype=ItemSubType.PERSON)
    returned_person_ids = {person.id for person in person_list_items}
    assert created_person_id in returned_person_ids, f"Person with ID {created_person_id} not in registry."

    # Study
    created_study = await create_item(client=client, item_subtype=ItemSubType.STUDY)
    created_study_id = created_study.id
    cleanup_items.append((ItemSubType.STUDY, created_study_id))

    study_list = await client.registry.study.list_items(list_items_payload=generic_list_request)
    study_list_items: List[ItemStudy] = assert_list_items(
        item=study_list, item_subtype=ItemSubType.STUDY)
    returned_study_ids = {study.id for study in study_list_items}
    assert created_study_id in returned_study_ids, f"Study with ID {created_study_id} not in registry."

    # Models
    created_model = await create_item(client=client, item_subtype=ItemSubType.MODEL)
    created_model_id = created_model.id
    cleanup_items.append((ItemSubType.MODEL, created_model_id))

    model_list = await client.registry.model.list_items(list_items_payload=generic_list_request)
    model_list_items: List[ItemModel] = assert_list_items(
        item=model_list, item_subtype=ItemSubType.MODEL)
    returned_model_ids = {model.id for model in model_list_items}
    assert created_model_id in returned_model_ids, f"Model with ID {created_model_id} not in registry."


@pytest.mark.asyncio
async def test_export_all_items_in_registry(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:
    """Creates an organisation (to have at least one item in registry) and exports all items
       in registry in a dump fashion (without pagination)"""

    created_organisation = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)
    created_org_id = created_organisation.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id))

    all_items_in_registry = await client.registry.admin.export_items()
    assert all_items_in_registry is not None, "Failed to export all items from the registry"
    assert all_items_in_registry.status.success, "Failed to export all items from registry."
    assert all_items_in_registry.items, "Failed to find 'items' within registry export"
    assert len(all_items_in_registry.items) > 0, "Registry export failed. Test showing zero items in registry \
                                                  There is at least one item present within registry,"

"""Listing Datastore Items and Registry Items - Pagination Present"""


@pytest.mark.asyncio
async def test_datastore_pagination(client: ProvenaClient, dataset_fixture: Tuple[str, str], cleanup_items: CLEANUP_ITEMS) -> None:
    """Testing datastore pagination across different use cases."""

    dataset_1_handle, dataset_2_handle = dataset_fixture

    """Testing generally"""
    list_dataset_request = NoFilterSubtypeListRequest(
        sort_by=None,
        pagination_key=None
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request)
    assert_list_items(item=dataset_list, item_subtype=ItemSubType.DATASET)

    """Testing with different sort criteria"""

    list_dataset_request = NoFilterSubtypeListRequest(
        sort_by=SortOptions(sort_type=SortType.DISPLAY_NAME,
                            ascending=True, begins_with=None),
        pagination_key=None
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request)
    dataset_list_items: List[ItemDataset] = assert_list_items(
        item=dataset_list, item_subtype=ItemSubType.DATASET)
    sorted_names = [item.display_name for item in dataset_list_items]
    assert sorted_names == sorted(
        sorted_names), "Datasets are not sorted by DISPLAY_NAME in ascending order"

    list_dataset_request_two = NoFilterSubtypeListRequest(
        sort_by=SortOptions(sort_type=SortType.CREATED_TIME,
                            ascending=True, begins_with=None),
        pagination_key=None
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request_two)
    dataset_list_items: List[ItemDataset] = assert_list_items(
        item=dataset_list, item_subtype=ItemSubType.DATASET)
    sorted_dates = [(item.created_timestamp) for item in dataset_list_items]
    assert sorted_dates == sorted(
        sorted_dates), "Datasets are not sorted by CREATED_TIME in ascending order"

    """Testing with different page sizes"""

    list_dataset_request_three = NoFilterSubtypeListRequest(
        sort_by=None,
        pagination_key=None,
        page_size=2
    )

    dataset_list = await client.datastore.list_datasets(list_dataset_request=list_dataset_request_three)
    dataset_list_items: List[ItemDataset] = assert_list_items(
        item=dataset_list, item_subtype=ItemSubType.DATASET)
    assert len(
        dataset_list_items) == 2, f"Dataset list exceed page size. Something is wrong!"


@pytest.mark.asyncio
async def test_registry_pagination(client: ProvenaClient, cleanup_items: CLEANUP_ITEMS) -> None:
    """Creates two organisation items and tests pagination logic and support."""

    created_organisation_1 = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)
    created_org_id_1 = created_organisation_1.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id_1))

    created_organisation_2 = await create_item(client=client, item_subtype=ItemSubType.ORGANISATION)
    created_org_id_2 = created_organisation_2.id
    cleanup_items.append((ItemSubType.ORGANISATION, created_org_id_2))

    sort_request = GeneralListRequest(
        filter_by=None,
        sort_by=SortOptions(sort_type=SortType.DISPLAY_NAME,
                            ascending=True, begins_with=None),
        pagination_key=None,
        page_size=100
    )

    sorted_organisation_list = await client.registry.organisation.list_items(list_items_payload=sort_request)
    sorted_organisation_list_items: List[ItemOrganisation] = assert_list_items(
        item=sorted_organisation_list, item_subtype=ItemSubType.ORGANISATION)
    sorted_names = [
        item.display_name for item in sorted_organisation_list_items]
    assert sorted_names == sorted(
        sorted_names), "Organisations are not sorted by DISPLAY_NAME in ascending order"

    sort_request.sort_by = SortOptions(
        sort_type=SortType.CREATED_TIME, ascending=True, begins_with=None)

    sorted_organisation_list = await client.registry.organisation.list_items(list_items_payload=sort_request)
    sorted_organisation_list_items: List[ItemOrganisation] = assert_list_items(
        item=sorted_organisation_list, item_subtype=ItemSubType.ORGANISATION)
    sorted_dates = [
        item.created_timestamp for item in sorted_organisation_list_items]
    assert sorted_dates == sorted(
        sorted_dates), "Organisations are not sorted by CREATED_TIME in ascending order"

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
    assert len(
        paged_organisation_list.items) == 2, "Paged organisation list exceeds page size. Something is wrong!"

"""Provenance - Registring Model Runs Etc.."""


@pytest.mark.asyncio
async def test_provenance_workflow(client: ProvenaClient, org_person_fixture: Tuple[ItemBase, ItemBase], dataset_fixture: Tuple[str, str], cleanup_items: CLEANUP_ITEMS) -> None:
    # prov test that will create the requirements needed for a model run record and register it
    # Procedure:
    # create the simple entities required (person, organisation)
    # register custom dataset templates for input and output datasets
    # register simple model
    # register model run workflow tempalte using references to pre registered entities
    # create and register the model run object using references to pre registered entitites

    # Create datasets needed for model runs
    dataset_1_handle, dataset_2_handle = dataset_fixture
    organisation, person = org_person_fixture

    # register custom dataset templates (input and output)
    input_template = await create_item(client=client, item_subtype=ItemSubType.DATASET_TEMPLATE)
    cleanup_items.append((ItemSubType.DATASET_TEMPLATE, input_template.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client=client,
        item=input_template,
        cleanup_items=cleanup_items
    )

    output_template = await create_item(client=client, item_subtype=ItemSubType.DATASET_TEMPLATE)
    cleanup_items.append((ItemSubType.DATASET_TEMPLATE, output_template.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client=client,
        item=output_template,
        cleanup_items=cleanup_items
    )

    # Register the model used in the model run
    model = await create_item(client=client, item_subtype=ItemSubType.MODEL)
    cleanup_items.append((ItemSubType.MODEL, model.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client=client,
        item=model,
        cleanup_items=cleanup_items
    )

    # create and register model run workflow template
    required_annotation_key = "annotation_key1"
    optional_annotation_key = "annotation_key2"
    mrwt_domain_info = ModelRunWorkflowTemplateDomainInfo(
        display_name="IntegrationTestMRWT",
        software_id=model.id,  # model is software
        input_templates=[TemplateResource(
            template_id=input_template.id, optional=False)],
        output_templates=[TemplateResource(
            template_id=output_template.id, optional=False)],
        annotations=WorkflowTemplateAnnotations(
            required=[required_annotation_key],
            optional=[optional_annotation_key]
        ),
        user_metadata=None
    )
    mrwt = await create_item_from_domain_info_successfully(
        client=client,
        item_subtype=ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE,
        domain_info=mrwt_domain_info)
    assert mrwt is not None, "Created Model Run Workflow Template is None"
    assert mrwt.created_item is not None, "Created Model Run Workflow Template does not contain created_item"
    assert mrwt.created_item.id is not None, "Created Model Run Workflow Template does not have handle ID"

    cleanup_items.append(
        (ItemSubType.MODEL_RUN_WORKFLOW_TEMPLATE, mrwt.created_item.id))

    # cleanup create activity
    await cleanup_create_activity_from_item_base(
        client=client,
        item=mrwt.created_item,
        cleanup_items=cleanup_items
    )

    # create model run to register
    model_run_record = ModelRunRecord(
        workflow_template_id=mrwt.created_item.id,
        inputs=[TemplatedDataset(
            dataset_template_id=input_template.id,
            dataset_id=dataset_1_handle,
            dataset_type=DatasetType.DATA_STORE,
            resources={"item_key": "some-key"}

        )],
        outputs=[TemplatedDataset(
            dataset_template_id=output_template.id,
            dataset_id=dataset_2_handle,
            dataset_type=DatasetType.DATA_STORE,
            resources={"item_key": "some-key"}
        )],
        associations=AssociationInfo(
            modeller_id=person.id,
            requesting_organisation_id=organisation.id
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
        client=client,
        model_run_record=model_run_record
    )

    model_run_id = response_model_run_record.id
    cleanup_items.append((ItemSubType.MODEL_RUN, model_run_id))

    # create model run to register including a linked study
    study = await create_item(
        client=client,
        item_subtype=ItemSubType.STUDY)
    cleanup_items.append((ItemSubType.STUDY, study.id))

    model_run_record.study_id = study.id

    # register model run
    response_model_run_record = await register_model_run_successfully(
        client=client,
        model_run_record=model_run_record
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
            target=study.id
        ),
        lineage_response=activity_upstream_query
    )

    # ensure invalid study id results in failure
    model_run_record.study_id = '1234'

    # register model run

    # Bad Request Exception since this is an invalid study ID
    with pytest.raises(BadRequestException):
        possible_model_run_record = await register_model_run_failure(
            client=client,
            model_run_record=model_run_record
        )

        if possible_model_run_record:
            model_run_id = possible_model_run_record.id
            cleanup_items.append((ItemSubType.MODEL_RUN, model_run_id))
            assert False, f"Model run registration with invalid study should have failed, but did not."
