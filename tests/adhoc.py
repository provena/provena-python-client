import json
from provenaclient import ProvenaClient, Config
from provenaclient.auth import DeviceFlow
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import NoFilterSubtypeListRequest, SortOptions, SortType
from ProvenaInterfaces.ProvenanceAPI import ModelRunRecord, TemplatedDataset, RegisterBatchModelRunRequest
from ProvenaInterfaces.ProvenanceModels import DatasetType, AssociationInfo
import asyncio
from provenaclient.auth.manager import Log
from typing import List
import os
import random


async def main() -> None:
    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    auth = DeviceFlow(keycloak_endpoint=config.keycloak_endpoint,
                      client_id="client-tools", log_level=Log.DEBUG)

    client = ProvenaClient(config=config, auth=auth)

    # fetch dummy dataset (see failure)
    # print("fetching bad")
    # try:
    #   await client.datastore.fetch_dataset(id="bad")
    # except Exception as e:
    #   print(f"Exception {e}")

    # fetch successful dataset (no failure)
    # print("fetching good")
    # res = await client.datastore.fetch_dataset(id="10378.1/1898010")
   # print(res.json(indent=2))

    # print("minting")
    # create_dataset = await client.datastore.mint_dataset(
    #    CollectionFormat(
    #        associations=CollectionFormatAssociations(
    #        organisation_id="10378.1/1893860",
    #        data_custodian_id="10378.1/1893843",
    #        point_of_contact= None
    #        ),
    #        approvals=CollectionFormatApprovals(
    #            ethics_registration = DatasetEthicsRegistrationCheck(relevant=False, obtained=False),
    #            ethics_access=DatasetEthicsAccessCheck(relevant= False, obtained= False),
    #            indigenous_knowledge=IndigenousKnowledgeCheck(relevant=False, obtained= False),
    #            export_controls=ExportControls(relevant=False, obtained=False)
    #        ),
    #        dataset_info=CollectionFormatDatasetInfo(
    #            name="Parth testing",
    #            description="testing dataset",
    #            access_info=AccessInfo(reposited=True, uri=None, description=None),
    #            publisher_id="10378.1/1893860",
    #            published_date=date.today(),
    #            license = "https://www.google.com", #type:ignore
    #            created_date=date.today(),
    #            purpose= None,
    #            rights_holder=None,
    #            usage_limitations=None,
    #            preferred_citation=None,
    #            formats = None,
    #            keywords= None,
    #            user_metadata= None,
    #            version = None
    #        )
    #    )
    # )
    # dataset = await client.datastore.fetch_dataset(id = str(create_dataset.handle))
    # print(dataset.json(indent=2))

    # search for datasets
    """
    print("searching")
    res = await client.datastore.search_datasets(
        query="coral",
        limit=50
    )
    print(res.json(indent=2))
    print(f"""
   # found {len(res.items) + len(res.auth_errors) + len(res.misc_errors)} total items.
   # found {len(res.items)} successful items
    # found {len(res.auth_errors)} auth error items
    # found {len(res.misc_errors)} misc error items
    """)
    
    # testing admin auth module 
    print("Listing all history")
    result = await client.auth_api.admin.get_all_request_history()
    print(result.json(indent=2))
    
    print("Listing all pending")
    result = await client.auth_api.admin.get_all_pending_request_history()
    print(result.json(indent=2))



    list_dataset_request =  NoFilterSubtypeListRequest(
            sort_by=SortOptions(sort_type=SortType.DISPLAY_NAME, ascending=False, begins_with=None), 
            pagination_key=None, 
            page_size=10
        )
    
    count = 0

    all_datasets = await client.datastore.list_all_datasets()

    for dataset in all_datasets:
        print(dataset.display_name)


    async for dataset in client.datastore.for_all_datasets(list_dataset_request, total_limit=19):
        count = count + 1 
        print(dataset.id)

    print(count)

    """

    # model_run = ModelRunRecord(
    #    workflow_template_id= "10378.1/1905251",
    #    model_version="1.0",
    #    inputs=[
    #        TemplatedDataset(
    #            dataset_template_id="10378.1/1905250",
    #            dataset_id="10378.1/1904961",
    #            dataset_type=DatasetType.DATA_STORE,
    #            resources= None

    #        )
    #    ],
    #    outputs=[
    #        TemplatedDataset(
    #            dataset_template_id="10378.1/1905250",
    #            dataset_id="10378.1/1900159",
    #            dataset_type=DatasetType.DATA_STORE,
    #            resources= None

    #        )
    #    ],
    #    annotations=None,
    #    display_name="Parth Model Run",
    #    description="Testing modl run parth",
    #    study_id=None,
    #    associations= AssociationInfo(
    #        modeller_id="10378.1/1893843",
    #        requesting_organisation_id= None
    #    ),
    #    start_time=0,
    #    end_time=1
    # )

    # list_of_model_runs = [model_run, model_run,  model_run]

    # list_y = json.loads(json.dumps([item.json() for item in list_of_model_runs]))

    # print(list_y)

    # batch = RegisterBatchModelRunRequest(records=[model_run])

    # res = await client.prov_api.convert_model_runs_to_csv_with_file(file_path="/home/parth/client_work/provena-python-client/7bd3e0e9-1a47-458b-820e-315f514c8640.csv")

    # print(res)

    # res = await client.prov_api.register_batch_model_runs(batch_model_run_payload= "7bd3e0e9-1a47-458b-820e-315f514c8640")

    # print(res)

    # This will not pass
    # res = await client.prov_api.regenerate_csv_from_model_run_batch(batch_id= "7bd3e0e9-1a47-458b-820e-315f514c8640", file_path="/path/does/not/exist", write_to_csv=True)
    # print(res)

    # This will pass
    # res = await client.prov_api.regenerate_csv_from_model_run_batch(batch_id="7bd3e0e9-1a47-458b-820e-315f514c8640", file_path=None, write_to_csv=True)
    # print(res)

    # await client.prov_api.generate_csv_template("10378.1/1905251")

    # res = await client.prov_api.admin.store_multiple_records(registry_record=list_of_model_runs)

    last: str = ""
    async for ds in client.datastore.for_all_datasets(
        list_dataset_request=NoFilterSubtypeListRequest(
            sort_by=SortOptions(sort_type=SortType.UPDATED_TIME,
                                ascending=False, begins_with=None),
            pagination_key=None),
    ):
        print(ds.id)
        last = ds.id

    output_path = "local_test"

    await client.datastore.io.download_all_files(
        destination_directory=output_path,
        dataset_id=last
    )

    # create a file
    def random_num() -> int: return random.randint(100, 1000)

    with open(f"{output_path}/testfile{random_num()}.txt", 'w') as f:
        f.write("Hello world!")
    with open(f"{output_path}/nested/testfile{random_num()}.txt", 'w') as f:
        f.write("Hello world!")

    await client.datastore.io.upload_all_files(
        source_directory=output_path,
        dataset_id=last
    )

    # list files
    files = await client.datastore.io.list_all_files(
        dataset_id=last,
        print_list=True
    )

asyncio.run(main())
