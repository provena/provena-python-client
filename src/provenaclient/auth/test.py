from provenaclient.auth.auth import DeviceFlow
import requests
import traceback

# Define the Keycloak endpoint and client ID
keycloak_url = "https://auth.dev.rrap-is.com/auth/realms/rrap"
client_id = "client-tools"

try:
    # Create the DeviceFlow object
    device_auth = DeviceFlow(keycloak_endpoint=keycloak_url, client_id=client_id)

    # Initialize the device flow which will open a web browser for user code input
    print("Initialization complete. Check your browser to authenticate.")

    auth = device_auth.get_auth

    response = requests.get(url = "https://registry-api.dev.rrap-is.com/admin/export"
                            ,auth= auth())
    
    print(response.json())
                    
except Exception as e:
    traceback.print_exc()
    print(f"An error occurred: {e}")
