import json

"""
Generates an enumeration of endpoints for a given openapi.json file. Can be used
to accelerate client development. Use as `python
generate_open_api_endpoint_dump.py`. Ensure the desired file is called
openapi.json in the working directory. The enum will be printed to the terminal
ready to be copy pasted into the application code.
"""

# Read the openapi.json spec file
with open("openapi.json", "r") as f:
    data = json.load(f)

# Start building the enum classes as strings
enum_class_general = 'class OpenAPIEndpoints(str, Enum):\n'
enum_class_general += '    """An ENUM containing the openapi api endpoints."""\n'

enum_class_admin = 'class OpenAPIAdminEndpoints(str, Enum):\n'
enum_class_admin += '    """An ENUM containing the openapi admin api endpoints."""\n'

# Iterate over paths in the openapi spec
for path, path_content in data.get('paths', {}).items():
    for method in path_content:

        # Generate the enum key by formatting URL as per requirements
        endpoint = method.upper() + path.replace('/', '_').replace('-', '_').upper()
        
        if path == "/":
            endpoint = "GET_HEALTH_CHECK"

        # Determine which enum class to add the endpoint to
        if "admin" in path:
            enum_class_admin += f"    {endpoint} = \"{path}\"\n"
        else:
            enum_class_general += f"    {endpoint} = \"{path}\"\n"

print(enum_class_general)
print()
print(enum_class_admin)
