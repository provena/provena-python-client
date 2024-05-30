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

# Start building the enum class as a string
enum_class = 'class OpenAPIEndpoints(str, Enum):\n'
enum_class += '    """An ENUM containing the openapi api endpoints."""\n'

# Iterate over paths in the openapi spec
for path, path_content in data.get('paths', {}).items():
    for method in path_content:

        # Generate the enum key by formatting URL as per requirements
        endpoint = method.upper() + path.replace('/', '_').replace('-','_').upper()
        
        if path == "/":
            endpoint = "GET_HEALTH_CHECK"

        # Add the endpoint to the enum class string
        enum_class += f"    {endpoint} = \"{path}\"\n"

print(enum_class)

print()