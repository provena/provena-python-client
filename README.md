# Provena Python Client

Welcome to the Provena Python Client repository! This client library is a programmatic interface designed to interact seamlessly with your Provena instance. It allows you to replicate most functionalities of the Provena Web app through Python code, including fetching or minting datasets, creating items within the registry, and launching provenance workflows. With the Provena Python Client, you can achieve comprehensive interactions with only a few lines of code.

## Core Technologies and Dependencies Used: 
- Python + MyPy
- Pydantic 
- Httpx 

Refer to [pyproject.toml](./pyproject.toml) for versioning info and information of other dependencies. 

## Getting Started

To install the Provena Python Client, simply use pip:

```bash
pip install provenaclient
```

Once you have successfully installed provenaclient, refer to the following Example Notebook here at: [Example Notebook](docs/example.ipynb) to start coding away!

## Testing

### Unit Tests

The Provena Python Client includes unit tests that check functionality using real server interactions and mocked components using `httpx_mock`. Tests cover HTTP methods, error handling, and JSON parsing.

**To run unit tests:**
1. Install dependencies from `pyproject.toml`.
2. Run `pytest test_unit.py` in the test directory.

### Integration Tests

The Provena Python Client includes integration tests that validate and assess the functioning of the client library and its interaction with Provena API's, focusing on dataset operations, entity searching, item fetching, and provenance lifecycle.

**To run integration tests:**
1. Install dependencies from `pyproject.toml`.
2. Set up necessary credentials in `.env` (contact Provena Development Team for setup).
3. Run `pytest test_integration.py` in the test directory.

For detailed testing procedures, see the [Testing Guide](tests/README.md).

## Documentation: 

Find Provena Python Client documentation and API Reference at: ([Provena Client Documentation](https://provena.github.io/provena-python-client/))

## Contact Information 
Contact Provena Developers via https://www.csiro.au/en/contact

## Contributing:
 TODO 

## License

`provenaclient` was created by Provena Development Team (CSIRO). Provena Development Team (CSIRO) retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.

## Acknowledgements
 The development of Provena Python Client was funded by Reef Restoration and Adaptation Program (RRAP), which is a partnership between the Australian Government’s Reef Trust and the Great Barrier Reef Foundation. Provena Python Client has been developed to support the Modelling and Decision Support (MDS) Subprogram (https://gbrrestoration.org/program/modelling-and-decision-support/).

 People who contributed and developed Provena Python Client (ordered alphabetically):
  - Jonathan Yu
  - Peter Baker
  - Parth Kulkarni
  - Ross Petridis