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

from integration_helpers import valid_collection_format_1, valid_collection_format_2, valid_collection_format_3
from provenaclient.utils.exceptions import BadRequestException

"""Pre-requiests before running unit tests: 

   1. You will need to setup token flow to be able to run these tests.
      For now I will use my tokens through device flow. 
   2. Creating various helper functions.

"""


"""Registering and Finding Dataset"""

@pytest.fixture
def auth_manager() -> DeviceFlow:

    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    return DeviceFlow(config=config, client_id="client-tools")

@pytest.fixture
def client(auth_manager: DeviceFlow) -> ProvenaClient:
    
    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    return ProvenaClient(config=config, auth=auth_manager)



async def _cleanup(client: ProvenaClient, list_of_handles: List[Tuple[ItemSubType, IdentifiedResource]]) -> None:
    for item_sub_type, handle in list_of_handles:
        delete_status_response = await client.registry.admin.delete(id=handle, item_subtype=item_sub_type)
        assert delete_status_response.status.success, f"Delete request has failed with details {delete_status_response.status.details}."


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
async def test_register_dataset(client: ProvenaClient) -> None:

    cleanup_items: List[Tuple[ItemSubType, IdentifiedResource]]

    """
     1. Need to find the dataset domain info, to get a dummy dataset 

    """

    valid_collection_formats: List[CollectionFormat] = [
        valid_collection_format_1,
        valid_collection_format_2
    ]

    for valid_cf in valid_collection_formats: 
        mint_response = await client.datastore.mint_dataset(dataset_mint_info=valid_cf)

        assert mint_response.status.success, "Reported failure when minting dataset"
        assert mint_response.handle, "Mint response does not contain a handle"
        cleanup_items.append((ItemSubType.DATASET, mint_response.handle))

    
        # Fetch dataset by created handle_id
        dataset_fetch_response = await client.datastore.fetch_dataset(mint_response.handle)
        dataset_fetch_item = dataset_fetch_response.item

        assert dataset_fetch_response.status.success, f"Reported failure when fetching dataset with id {mint_response.handle}"
        assert dataset_fetch_item is not None, "Fetched Dataset is null/none"
        assert dataset_fetch_item.id == mint_response.handle

        """So everytime some entity is registred for the first time, by default a create activity is created
           which is launched through the job-api.
           
           1. We will take the create_activity_session_id, and keep polling on it to see if its completed. 

           This is currently TODO because registry fetch across all aspects needs to be completed.

        """

        # Ensure the workflow links were updated
        assert dataset_fetch_item.workflow_links
        assert dataset_fetch_item.workflow_links.create_activity_workflow_id

        assert mint_response.register_create_activity_session_id

        create_activity_response = await client.job_api.await_successful_job_completion(
                session_id=mint_response.register_create_activity_session_id
        )

        # Now we have to assert if the id exists

        assert create_activity_response.result is not None
        parsed_result = RegistryRegisterCreateActivityResult.parse_obj(
            create_activity_response.result)
        
        lodge_session_id = parsed_result.lodge_session_id
        creation_activity_id = parsed_result.creation_activity_id

         # Clean up dataset Create side effect
        cleanup_items.append(
            (ItemSubType.CREATE, creation_activity_id))

        # Wait for next step of lifecycle - step 2
        # no meaningful response from this - just check success
        await client.job_api.await_successful_job_completion(
            session_id=lodge_session_id
        )

        # - check the Create activity was produced and is accurate
        fetched_create_activity_response = await client.registry.create_activity.fetch(
            id = creation_activity_id
        )

        assert fetched_create_activity_response.item
        assert fetched_create_activity_response.item.id == dataset_fetch_item
    
    await _cleanup(client = client, list_of_handles=cleanup_items)


"""Listing items that is present."""

@pytest.mark.asyncio
async def list_all_datasets(client: ProvenaClient) -> None: 

    datasets = await client.datastore.list_all_datasets()
    assert datasets is not None
    assert len(datasets) > 0

    
"""Search-API related tests and finding newly related items."""


@pytest.mark.asyncio
async def test_searching_items_in_registry(client: ProvenaClient) -> None:

    valid_collection_formats: List[CollectionFormat] = [
        valid_collection_format_1
    ]

    cleanup_items: List[Tuple[ItemSubType, IdentifiedResource]] = []

    dataset_handles = []
    for valid_cf in valid_collection_formats: 
        mint_response = await client.datastore.mint_dataset(dataset_mint_info=valid_cf)

        assert mint_response.status.success, "Reported failure when minting dataset"
        assert mint_response.handle, "Mint response does not contain a handle"
        cleanup_items.append((ItemSubType.DATASET, mint_response.handle))
        dataset_handles.append(mint_response.handle)

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

        # Now we have to assert if the id exists

        assert create_activity_response.result is not None
        parsed_result = RegistryRegisterCreateActivityResult.parse_obj(
            create_activity_response.result)
        
        lodge_session_id = parsed_result.lodge_session_id
        creation_activity_id = parsed_result.creation_activity_id

         # Clean up dataset Create side effect
        cleanup_items.append(
            (ItemSubType.CREATE, creation_activity_id))

        # Wait for next step of lifecycle - step 2
        # no meaningful response from this - just check success
        await client.job_api.await_successful_job_completion(
            session_id=lodge_session_id
        )

        # - check the Create activity was produced and is accurate
        fetched_create_activity_response = await client.registry.create_activity.fetch(
            id = creation_activity_id
        )

        assert fetched_create_activity_response.item
        assert fetched_create_activity_response.item.id == dataset_fetch_item

    
    # Create items within registry of different types


    # 

    # Perform search using the dataset handles
    for dataset_handle in dataset_handles:
        search_response = await client.search.search_registry(query=dataset_handle, subtype_filter=None, limit = None)

        assert search_response.status.success, f"Search failed for dataset handle {dataset_handle}"
        assert search_response.results
        assert dataset_handle in search_response.results
    
    await _cleanup(client = client, list_of_handles=cleanup_items)



"""Querying Provenance"""





