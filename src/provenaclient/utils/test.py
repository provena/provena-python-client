from .Auth import DeviceFlow

def main():
    # Define the Keycloak endpoint and client ID
    keycloak_url = "https://auth.dev.rrap-is.com/auth/realms/rrap"
    client_id = "client-tools"

    try:
        # Create the DeviceFlow object
        device_auth = DeviceFlow(keycloak_endpoint=keycloak_url, client_id=client_id)
        
        # Initialize the device flow which will open a web browser for user code input
        device_auth.init()


        print("Initialization complete. Check your browser to authenticate.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()