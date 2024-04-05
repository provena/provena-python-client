# provenaclient

A client library for interfacing with a Provena instance.

## Installation

```bash
$ pip install provenaclient
```

## Usage

### How to get started with Poetry

1) Run the Command: `curl -sSL https://install.python-poetry.org | python3 -`.
2) Check if poetry was successfully installed by running `poetry --version`.
3) You should now have be able to see your poetry version successfully. 
4) Now run the command `poetry shell`. This  will activate the poetry virtual environment for you.
5) Now finally run the command `poetry install`. This will install all dependencies defined within pyproject.toml.

### My Poetry Installation is not being detected?
1) This means that your PATH variable does not include the Poetry directory. 
2) Open your .bashrc file, using the command `nano ~/.bashrc`.
3) Add the following line at the end of the file, `export PATH= "$HOME/.local/bin:$PATH"`.
4) Reload your .bashrc file, using the command `source ~/.bashrc`.
5) Verify that your poetry is now running, using the command `poetry --version`.



## Contributing
TODO

## License

`provenaclient` was created by Provena Development Team (CSIRO). Provena Development Team (CSIRO) retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.

## Credits

`provenaclient` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
