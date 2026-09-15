This docs directory is used to build the GH pages that appear on https://provena.github.io/provena-python-client/.

# Build

We use Sphinx to build the HTML files from these source files.

To build, we can use either `make.sh` (linux or git bash), `make.bat` (windows), `Makefile` (depends on make).

## make.sh

```
$ virtualenv .venv
$ source .venv/bin/activate # or on Git bash on windows $ source .venv/Scripts/activate
$ pip install -r requirements.txt
$ ./make.sh
```

## make.bat

This assumes you're on a Windows Command Prompt

```
> virtualenv .venv
> pip install -r requirements.txt
> source .venv/Scripts/activate
> ./make.bat HTML
```

## Makefile

This assumes you have `make` installed

```
$ make HTML
```

# Copy over files

Once the docs are built, you will need to checkout a copy of the provena-python-client repo on the `gh-pages`. 
Copy over the files from the build directory (e.g. `_build`) to the checked out repo.

Create a pull request for it.

Once the PR is accepted, Github will update the pages and the docs should appear on
https://provena.github.io/provena-python-client/