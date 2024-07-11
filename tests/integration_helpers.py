
from datetime import date
from typing import cast
from ProvenaInterfaces.RegistryModels import *
from ProvenaInterfaces.RegistryAPI import *
from ProvenaInterfaces.SearchAPI import *

from provenaclient.modules.provena_client import ProvenaClient
from provenaclient.utils.registry_endpoints import *
from provenaclient.modules import Registry
from test_config import RouteParameters, route_params, non_test_route_params

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
    
    if item_subtype == ItemSubType.MODEL:
        example_model_domain_info = get_item_subtype_domain_info_example(item_subtype=item_subtype)
        example_model_domain_info = cast(ModelDomainInfo, example_model_domain_info)

        created_model = await client.registry.model.create_item(create_item_request=example_model_domain_info)
        return created_model

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
