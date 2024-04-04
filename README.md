# provenaclient

A client library for interfacing with a Provena instance.

## Installation

```bash
$ pip install provenaclient
```

## Usage

### How to get started with Poetry

1) Run the Command: `curl -sSL https://install.python-poetry.org | python3 -`
2) Check if poetry was succesfully installed by running `poetry --version`
3) You should now have be able to see your poetry version successfully. 

### My Poetry Installation is not being detected?
1) This means that your PATH variable does not include the Poetry directory. 
2) Open your .bashrc file, using the command `nano ~/.bashrc`
3) Add the following line at the end of the file, `export PATH= "$HOME/.local/bin:$PATH"`
4) Reload your .bashrc file, using the command `source ~/.bashrc`
5) Verify that your poetry is now running, using the command `poetry --version`



## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`provenaclient` was created by Parth Kulkarni. Parth Kulkarni retains all rights to the source and it may not be reproduced, distributed, or used to create derivative works.

## Credits

`provenaclient` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
