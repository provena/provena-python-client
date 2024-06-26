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

from typing import Any, List
import pytest
import pytest_asyncio
import httpx

from provenaclient.auth import DeviceFlow
from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.utils.config import Config

from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *

from integration_helpers import valid_collection_format_1, valid_collection_format_2, valid_collection_format_3

"""Pre-requiests before running unit tests: 

   1. You will need to setup token flow to be able to run these tests.
      For now I will use my tokens through device flow. 
   2. Creating various helper functions.

"""


"""Registering and Finding Dataset"""

@pytest.fixture
def mock_auth_manager() -> DeviceFlow:

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

@pytest.mark.asyncio
async def test_register_dataset(client: ProvenaClient) -> None:

    clean_up_items: List[Any] = []

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
        clean_up_items.append(mint_response.handle)

    
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

        assert mint_response.register_create_activity_session_id

        create_activity_response = await client.job_api.await_successful_job_completion(
                session_id=mint_response.register_create_activity_session_id
        )

        # Now we have to assert if the id exists

        assert create_activity_response.result is not None

        fetched_create_activity =
        assert fetched_create_activity.created_item_id == dataset_fetch_item.id

        lodge_session_id = create_activity_response.

        """



@pytest.mark.asyncio
async def list_all_datasets(client: ProvenaClient) -> None: 

    datasets = await client.datastore.list_all_datasets()
    assert datasets is not None
    assert len(datasets) > 0
    
"""Search-API related tests and finding newly related items."""

@pytest.mark.asyncio
async def searching_items_in_registry(client: ProvenaClient) -> None:
    # Register datasets to be searched
    clean_up_items: List[str] = []

    valid_collection_formats: List[CollectionFormat] = [
        valid_collection_format_1,
        valid_collection_format_2
    ]

    dataset_handles = []
    for valid_cf in valid_collection_formats: 
        mint_response = await client.datastore.mint_dataset(dataset_mint_info=valid_cf)

        assert mint_response.status.success, "Reported failure when minting dataset"
        assert mint_response.handle, "Mint response does not contain a handle"
        dataset_handles.append(mint_response.handle)
        clean_up_items.append(mint_response.handle)

        # Fetch dataset by created handle_id
        dataset_fetch_response = await client.datastore.fetch_dataset(mint_response.handle)
        dataset_fetch_item = dataset_fetch_response.item

        assert dataset_fetch_response.status.success, f"Reported failure when fetching dataset with id {mint_response.handle}"
        assert dataset_fetch_item is not None, "Fetched Dataset is null/none"
        assert dataset_fetch_item.id == mint_response.handle

    # Perform search using the dataset handles
    for dataset_handle in dataset_handles:
        search_response = await client.search.search_registry(query=dataset_handle, subtype_filter=None, limit = None)

        assert search_response.status.success, f"Search failed for dataset handle {dataset_handle}"
        







