import asyncio
from provenaclient.auth.auth import DeviceFlow
from provenaclient.utils.config import Config
from provenaclient.modules.provena_client import ProvenaClient
from ProvenaInterfaces.RegistryModels import *

async def main() -> None:

    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    auth = DeviceFlow(keycloak_endpoint=config.keycloak_endpoint, client_id="client-tools")

    client = ProvenaClient(config=config, auth=auth)

    create_dataset = await client.datastore.mint_dataset(
        CollectionFormat(
            associations=CollectionFormatAssociations(
            organisation_id="10378.1/1893860",
            data_custodian_id="10378.1/1893843",
            point_of_contact= None
            ),
            approvals=CollectionFormatApprovals(
                ethics_registration = DatasetEthicsRegistrationCheck(relevant=False, obtained=False),
                ethics_access=DatasetEthicsAccessCheck(relevant= False, obtained= False),  
                indigenous_knowledge=IndigenousKnowledgeCheck(relevant=False, obtained= False),
                export_controls=ExportControls(relevant=False, obtained=False)
            ),
            dataset_info=CollectionFormatDatasetInfo(
                name="Parth testing",
                description="testing dataset",
                access_info=AccessInfo(reposited=True, uri=None, description=None),
                publisher_id="10378.1/1893860",
                published_date=date.today(),
                license = "https://www.google.com", #type:ignore
                created_date=date.today(), 
                purpose= None, 
                rights_holder=None, 
                usage_limitations=None, 
                preferred_citation=None,
                formats = None, 
                keywords= None, 
                user_metadata= None, 
                version = None
            )
        )
    )


    dataset = await client.datastore.fetch_dataset(id = str(create_dataset.handle))

    print(dataset)


   

asyncio.run(main())
