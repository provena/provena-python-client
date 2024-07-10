
from datetime import date
from typing import cast
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.SearchAPI import *

from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.utils.registry_endpoints import *
from provenaclient.modules import Registry
from test_config import RouteParameters, route_params, non_test_route_params

valid_collection_format_1 = CollectionFormat(
    associations=CollectionFormatAssociations(
        organisation_id="10378.1/1893860",  
        data_custodian_id="10378.1/1893843",  
        point_of_contact="contact1@example.com"
    ),
    approvals=CollectionFormatApprovals(
        ethics_registration=DatasetEthicsRegistrationCheck(relevant=True, obtained=True),
        ethics_access=DatasetEthicsAccessCheck(relevant=True, obtained=True),
        indigenous_knowledge=IndigenousKnowledgeCheck(relevant=False, obtained=False),
        export_controls=ExportControls(relevant=True, obtained=True)
    ),
    dataset_info=CollectionFormatDatasetInfo(
        name="Integration Testing DiD I make it 1",
        description="Integration test dataset variation 1",
        access_info=AccessInfo(reposited=True, uri=None, description=None), #type:ignore
        publisher_id="10378.1/1893860",  
        published_date=date(2024, 6, 1),
        license="https://opensource.org/licenses/Apache-2.0",  # type:ignore
        created_date=date(2024, 6, 1),
        purpose="Testing variation 1",
        rights_holder="Rights Holder 1",
        usage_limitations="Limitations 1",
        preferred_citation="Citation 1",
        formats=["JSON", "YAML"],
        keywords=["integration", "test", "variation1"],
        user_metadata={"author": "Tester Variation 1"},
        version=None
    )
)

valid_collection_format_2 = CollectionFormat(
    associations=CollectionFormatAssociations(
        organisation_id="10378.1/1893860",  
        data_custodian_id="10378.1/1893843",  
        point_of_contact="contact2@example.com"
    ),
    approvals=CollectionFormatApprovals(
        ethics_registration=DatasetEthicsRegistrationCheck(relevant=False, obtained=False),
        ethics_access=DatasetEthicsAccessCheck(relevant=False, obtained=False),
        indigenous_knowledge=IndigenousKnowledgeCheck(relevant=True, obtained=True),
        export_controls=ExportControls(relevant=False, obtained=False)
    ),
    dataset_info=CollectionFormatDatasetInfo(
        name="Dataset Variation 2",
        description="Integration test dataset variation 2",
        access_info=AccessInfo(reposited=False, uri="https://example.com.au", description="Example Integration Test"), #type:ignore
        publisher_id="10378.1/1893860",  
        published_date=date(2024, 6, 2),
        license="https://opensource.org/licenses/MIT",  # type:ignore
        created_date=date(2024, 6, 2),
        purpose="Testing variation 2",
        rights_holder="Rights Holder 2",
        usage_limitations="No limitations",
        preferred_citation="Citation 2",
        formats=["CSV", "XML"],
        keywords=["integration", "test", "variation2"],
        user_metadata={"author": "Tester Variation 2"},
        version=None
    )
)


valid_collection_format_3 = CollectionFormat(
    associations=CollectionFormatAssociations(
        organisation_id="10378.1/1893860",  
        data_custodian_id="10378.1/1893843",  
        point_of_contact="contact3@example.com"
    ),
    approvals=CollectionFormatApprovals(
        ethics_registration=DatasetEthicsRegistrationCheck(relevant=True, obtained=True),
        ethics_access=DatasetEthicsAccessCheck(relevant=False, obtained=False),
        indigenous_knowledge=IndigenousKnowledgeCheck(relevant=False, obtained=False),
        export_controls=ExportControls(relevant=True, obtained=True)
    ),
    dataset_info=CollectionFormatDatasetInfo(
        name="Dataset Variation 3",
        description="Integration test dataset variation 3",
        access_info=AccessInfo(reposited=True, uri=None, description=None), #type:ignore
        publisher_id="10378.1/1893860",
        published_date=date(2024, 6, 3),
        license="https://opensource.org/licenses/GPL-3.0",  # type:ignore
        created_date=date(2024, 6, 3),
        purpose="Testing variation 3",
        rights_holder="Rights Holder 3",
        usage_limitations="No restrictions",
        preferred_citation="Citation 3",
        formats=["PDF", "DOCX"],
        keywords=["integration", "test", "variation3"],
        user_metadata={"author": "Tester Variation 3"},
        version=None
    )
)


valid_model_domain_info=[
                ModelDomainInfo(
                    display_name="Example model",
                    name="Example model",
                    description="This is a fake model",
                    documentation_url="https://example_model.org", #type:ignore
                    source_url="https://example_model.org",#type:ignore
                    user_metadata={
                        "my custom": "annotation",
                        "another custom": "annotation"
                    }
                ),
                ModelDomainInfo(
                    display_name="Example model updated",
                    name="Example model updated",
                    description="This is a fake updated model",
                    documentation_url="https://example_model.org",#type:ignore
                    source_url="https://example_model.org",#type:ignore
                    user_metadata={
                        "my updated custom": "annotation",
                    }
                )
            ]

valid_organisation_domain_info = [

        OrganisationDomainInfo(
            display_name="Example Organisation - Integration Tests",
            name = "Example organisation - Integration Tests",
            user_metadata = {
                "my custom org": "annotation",
                "another custom key": "annotation"
            },
            ror = None
        ), 
        OrganisationDomainInfo(
            display_name="Example Organisation 2 - Integration Tests",
            name = "Example organisation 2 - Integration Tests",
            user_metadata = {
                "my custom org": "annotation",
                "another custom key": "annotation"
            },
            ror = None
        ), 
]

CLEANUP_ITEMS = List[Tuple[ItemSubType, IdentifiedResource]]

async def create_organisation(client: ProvenaClient) -> OrganisationCreateResponse:

    example_org_domain_info = get_item_subtype_domain_info_example(item_subtype=ItemSubType.ORGANISATION)
    example_org_domain_info = cast(OrganisationDomainInfo, example_org_domain_info)

    created_org = await client.registry.organisation.create_item(create_item_request=example_org_domain_info)
    return created_org
    

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


    return None

async def cleanup_helper(client: ProvenaClient, list_of_handles: CLEANUP_ITEMS) -> None:
    for item_sub_type, handle in list_of_handles:
        delete_status_response = await client.registry.admin.delete(id=handle, item_subtype=item_sub_type)
        assert delete_status_response.status.success, f"Delete request has failed with details {delete_status_response.status.details}."

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