import asyncio
from provenaclient.utils.Auth import DeviceFlow
from provenaclient.utils.Config import Config
from provenaclient.modules.ProvenaClient import ProvenaClient

async def main() -> None:

    config = Config(
        domain="dev.rrap-is.com",
        realm_name="rrap"
    )

    auth = DeviceFlow(keycloak_endpoint=config.keycloak_endpoint, client_id="client-tools")

    client = ProvenaClient(config=config, auth=auth)

    dataset = await client.datastore.fetch_item(id = "10378.1/1888975")

asyncio.run(main())
