import json

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
