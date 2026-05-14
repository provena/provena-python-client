# Quickstart

## Initialising the provena client

To use the provena client, you will need to provide both `auth` and `config` objects
to select the authentication method, and configuration details for the 
Provena instance you would like to interface with. 

Replace `my-provena.cloud` with the URL of the Provena instance and change `realm_name` value
to the appropriate Keycloak realm.
```
client_config = Config(
        domain="my-provena.cloud",
        realm_name="provena"
    )
auth = DeviceFlow(config=client_config, client_id="client-tools")

client = ProvenaClient(auth=auth, config=client_config)
await client.datastore.get_health_check()
```

## Finding and searching items from the Registry


### Fetching items from the Registry

You can fetch any item from the Registry using `general_fetch_item()` and the id of the item. 

```
res = await client.registry.general_fetch_item(id=id)
print(f"{res.item['display_name']} {res.item['item_subtype']}")
```

Each sub-type has an associated `fetch()` too.
```
res = await client.registry.model_run.fetch(id=id)
```

You can use the ID of an item if you know ahead of time, or you can list them.

### Listing items in the Registry

#### General list function

You can list items from the Registry using `list_general_registry_items()`. 
This function expects an instance of `GeneralListRequest`
and  returns a generic result list. 

```
from ProvenaInterfaces.RegistryAPI import GeneralListRequest
general_list_request = GeneralListRequest(
    filter_by=None,
    sort_by=None,
    pagination_key=None
)

res = await client.registry.list_general_registry_items(general_list_request)
```

#### Sub-type list function

You can also list item from the sub-type modules via `list_items()`. In this case, it will only return a list of 
registry items of that sub-type. You may need to cast the returned object into Responses using the 
pydantic `parse_obj_as()`.

```
from pydantic import parse_obj_as

list_model_run_workflow = await client.registry.model_run_workflow.list_items(list_items_payload=general_list_request)
model_run_workflow_templates = parse_obj_as(ModelRunWorkflowTemplateListResponse, list_model_run_workflow)

print(f"Found {model_run_workflow_templates.total_item_count} model_run_workflow_templates")
```

Iterate over the list response like so.
```
for item in model_run_workflow_templates.items:
    m = parse_obj_as(ItemModelRunWorkflowTemplate, item)
    print(m)
```

#### Listing dataset items 

Datasets are special. List them this way from the client library's `datastore` module.
```
list_dataset = await client.datastore.list_all_datasets()
print(f"Found {len(list_dataset)} datasets")
for item in list_dataset:
    d = parse_obj_as(ItemDataset, item)
    print(d)
```

### Search for items

Provena provides a general search engine to search all items in the Registry. 
Currently the search results return a `QueryResult` object with:
 * `status` (Search result success or failure with `success` and `details` attributes)
 * `results` (list of results of `id` and `score` attributes for each result)
 * `warnings`

```
qres = await client.search.search_registry(query="fire", limit=10, subtype_filter=ItemSubType.DATASET)
assert qres.status.success
for r in qres.results:
    print(f"{r.id} {r.score}")
```

* `subtype_filter` can be `None` if you want to search over all subtypes
* `limit` can also be `None` to unrestrict the number of returned items

Using the returned `id` for a result, you can issue a fetch request (see above).


## Registering

Registering items creates an object in the registry with required metadata/payload values and 
issues a unique ID (via Handle).

See the following Provena docs section for more info on the Registry: [https://docs.provena.io/registry/](https://docs.provena.io/registry/)

### Registering datasets

Background information about registering a dataset in Provena is found here:
[https://docs.provena.io/data-store/registering-a-dataset.html](https://docs.provena.io/data-store/registering-a-dataset.html)

Minting a dataset.

```
register_response = await client.datastore.mint_dataset(dataset_mint_info=metadata)
assert register_response.status.success
print(f"Created Dataset Handle: {register_response.handle}. Access entity link: https://hdl.handle.net/{register_response.handle}")
```

The dataset may already exists and instead of minting, you may want to version it. Find out more about
versioning here: [https://docs.provena.io/versioning/versioning-overview.html](https://docs.provena.io/versioning/versioning-overview.html)

First we must find the latest version of the dataset. 
One way to do this would be to use the following function. 
```
async def latest_version_of_dataset(dataset_id):
    fetch_resp = await client.datastore.fetch_dataset(id=dataset_id)
    if fetch_resp.item.versioning_info.next_version == None or fetch_resp.item.versioning_info.next_version == "":
        #assume this was the latest version
        return dataset_id
    else:
        latest_version = await latest_version_of_dataset(fetch_resp.item.versioning_info.next_version)
        return latest_version
```

Then apply that function... 
```
print(f"Find the latest version of this dataset {dataset_item.id}")
latest_version = await latest_version_of_dataset(dataset_item.id)    
#use the latest_version id for the version request
version_request = VersionRequest(
        id=latest_version,
        reason="Updating dataset"
)
register_response = await client.datastore.version_dataset(version_request=version_request)
print(f"New Version of Dataset Handle: {register_response.new_version_id}. Access entity link: https://hdl.handle.net/{register_response.new_version_id}")
```

This creates a new dataset with its metadata copied over. We will then update the dataset metadata.
```
register_response = await client.datastore.update_dataset_metadata(handle_id=register_response.new_version_id, 
                                                                       reason="Updating metadata for new version", 
                                                                       metadata_payload=metadata)
```                                                                       



### Registering a model run 


Build the payload
```
from ProvenaInterfaces.ProvenanceAPI import ModelRunRecord, TemplatedDataset, DatasetType, AssociationInfo
from ProvenaInterfaces.AsyncJobAPI import JobStatus

# Building the Model Run Payload.
model_run_payload = ModelRunRecord(
    workflow_template_id=model_run_workflow_template_item.id,
    model_version = None, 
    inputs = [
        TemplatedDataset(
            dataset_template_id=input_dataset_template_item.id, 
            dataset_id=input_dataset_item.id,
            dataset_type=DatasetType.DATA_STORE
        )
    ], 
    outputs=[
        TemplatedDataset(
            dataset_template_id=output_dataset_template_item.id, 
            dataset_id=output_dataset_item.id,
            dataset_type=DatasetType.DATA_STORE
        )
    ], 
    annotations=None,
    display_name="Notebook Model Run Testing",
    description="Standard Provena Model Run Example",
    study_id=None,
    associations=AssociationInfo(
        modeller_id=person_item.id,
        requesting_organisation_id=organisation_item.id
    ),
    start_time=start_time,
    end_time=end_time
)
```

Register the payload
```
model_run_register_result = await client.prov_api.register_model_run(model_run_payload=model_run_payload)
```

```
# Check the response of the model run registration
print("Status of registration", model_run_register_result.status)
print("Job Session ID", model_run_register_result.session_id)
```

```
# Check the job to see if it's complete. We will do this by polling the job_api
job_result = await client.job_api.await_successful_job_completion(session_id=model_run_register_result.session_id)

while job_result.status != JobStatus.SUCCEEDED: # Keep polling on this cell till this turns to "SUCCEEDED"
    
    job_result = await client.job_api.await_successful_job_completion(session_id=model_run_register_result.session_id)
    pprint(job_result.result)
    pprint(job_result.job_type)


print()
print("Current job status:", job_result.status) 
```

Inspect the result of a successful model run record registration.
```
from pprint import pprint
model_run_record = job_result.result["record"]
pprint(model_run_record)
```

To understand more about what it means to register a model run, see [https://docs.provena.io/provenance/registering-model-runs/registration-process/overview.html](https://docs.provena.io/provenance/registering-model-runs/registration-process/overview.html).

### Registering other items via the Registry

Other than Dataset and Model Run, registering all other registry subtypes is straightforward.
You will need to instantiate the relevant DomainInfo payload.
Then use the sub-type module in the registry client module to create the item.

We will show a workflow for a "Model" sub-type below, however, you can substitute this for other types,
i.e. Dataset Template, Model Run Workflow Template, Organisation, Person, Study. 

First build the DomainInfo payload for the `Model` subtype using `ModelDomainInfo`.
```
from ProvenaInterfaces.RegistryModels import *

model_payload = ModelDomainInfo(
    display_name=model_item_payload['display_name'], 
    name=model_item_payload['name'] , 
    description=model_item_payload['description'],
    documentation_url=model_item_payload['documentation_url'], 
    source_url=model_item_payload['source_url'], 
    user_metadata=model_item_payload['user_metadata']
    )
```

Register the `Model` subtype instance via `create_item()`.
```
model_register_result = await client.registry.model.create_item(create_item_request=model_payload)
assert model_register_result.status.success
```

Just like a `Dataset`, the item may already exists and instead of creating the item, you may want to version it. Find out more about
versioning here: [https://docs.provena.io/versioning/versioning-overview.html](https://docs.provena.io/versioning/versioning-overview.html)

First we must find the latest version of the item. One way to do this would be to use the following function. 
We will continue using the `Model` example.

One way to find the latest version of the item for the `Model` subtype is:
```
async def latest_version_of_model(item_id):
    fetch_resp = await client.registry.model.fetch(id=item_id)
    if fetch_resp.item.versioning_info.next_version == None or fetch_resp.item.versioning_info.next_version == "":
        #assume this was the latest version
        return item_id
    else:
        latest_version = await latest_version_of_model(fetch_resp.item.versioning_info.next_version)
        return latest_version
```

We can then apply `latest_version_of_model()` in the steps to register a new version of the `Model`.

```
latest_version = await latest_version_of_model(model_item.id)
print(f"Find the latest version of this  {model_item.id}")
latest_version = await latest_version_of_model(model_item.id)    
print(f"Latest version: {latest_version}")
#use the latest_version id for the version request
version_request = VersionRequest(
   id=latest_version,
   reason="Updating model"
)
register_response = await client.registry.model.version_item(version_request=version_request)
print(f"New Version of Model Handle: {register_response.new_version_id}. Access entity link: https://hdl.handle.net/{register_response.new_version_id}")

#update the metadata
register_response = await client.registry.model.update(id=register_response.new_version_id, 
                                                                       reason="Updating metadata for new version", 
                                                                       domain_info=model_payload)
```