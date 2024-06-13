from provenaclient import ProvenaClient, Config
from provenaclient.auth import DeviceFlow
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import NoFilterSubtypeListRequest, SortOptions, SortType
import asyncio


async def main() -> None:
    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    auth = DeviceFlow(keycloak_endpoint=config.keycloak_endpoint,
                      client_id="client-tools")

    client = ProvenaClient(config=config, auth=auth)

    # fetch dummy dataset (see failure)
    #print("fetching bad")
    #try:
     #   await client.datastore.fetch_dataset(id="bad")
    #except Exception as e:
     #   print(f"Exception {e}")

    # fetch successful dataset (no failure)
    #print("fetching good")
    ###res = await client.datastore.fetch_dataset(id="10378.1/1898010")
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
    #found {len(res.auth_errors)} auth error items
    #found {len(res.misc_errors)} misc error items
    """)
    
    # testing admin auth module 
    print("Listing all history")
    result = await client.auth_api.admin.get_all_request_history()
    print(result.json(indent=2))
    
    print("Listing all pending")
    result = await client.auth_api.admin.get_all_pending_request_history()
    print(result.json(indent=2))

    """

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





asyncio.run(main())
