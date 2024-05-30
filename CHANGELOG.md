# CHANGELOG



## v0.1.0 (2024-05-30)

### Feature

* feat: implement datastore, search and auth client. ([`f33d689`](https://github.com/provena/provena-python-client/commit/f33d689622d5905c7a5f77b5c8b1e0b00f3b6b6e))

### Unknown

* Last attempt to make sphinx-auto-api work with CI job. ([`20b0819`](https://github.com/provena/provena-python-client/commit/20b08199bb0a2a2b33354dd957523eb9606dd8d7))

* Updating sphinx-autoapi dependency version due to CI failure. ([`d464c31`](https://github.com/provena/provena-python-client/commit/d464c316ecb0abc07f5ba602844585133bb38af1))

* JIRA 1669 &amp; 1677 Major: Implementing datastore interface &amp; functionality of fetch and create dataset.   (#3)

* Created directory structure.

* Initial structure of everything so far. I have been working on fleshing out the Auth interface as suggested by Peter, and made some progress.

* Completion of Device Flow for Auth Class, and also created a separate. API client that wraps around request library for better testing of auth interface in the future.

* Config Inteface, still needs to be reviewed. Furthermore, a decision needs to be made on how the endpoints are exposed to the user.

Co-authored-by: Ross (Laz) Petridis &lt;Rosspet@users.noreply.github.com&gt;

* Pushing latest changes so Ross can branch off my branch for his offline flow development.

* requirements conflict resolution

* Completed base auth interface + device flow, and provided more type safety to the auth device flow methods.

Completed config interface file with docstrings and updated CI-CD script to only run on main.

* feat(datastore): datastore fetch dataset functionality.

Implemented datastore fetch using the designed layers. Remaning work to design the custom exceptions and require review from others.

* (Still In Progress ): Implementing custom Exceptions for various edge cases when recieving  a response.

* Merging main into datastore-interface branch for easier development.

* Deleted redundant files. Due to file name change  on main there were duplicate files that were not removed during merge.

* (In Progress): Worked on mint dataset and fetch dataset functionality with the client library.

Facing some mypy issues and code needs to be reviewed for further enhancements.

* (FEAT): Completed datastore functionality with fetch and create dataset and also updated CI/CD scripts to push to pypi and made them separated.

* Reverted back to old ci-cd script setup as it would have ran in parallel instead of sequentially.

* Updated ci-cd script to only run on pull requests is  merged with base branch.

* Improved robustness of JSON parsing from response object and created a list of exceptions for better clarity.

* Removed requirements.txt

* Proposed changes and additional functionality (#4)

* Adding some additional poetry help in readme

* Implements streamlined helper functions which are stacked/modular.

Simplifies error parsing in L2.

Applies formatting changes and other minor changes.

* Improving file layout, adding convenience exports on key __init__.py files, moving testing out of import runway etc

* Adding search L1, L2, L3. Adding search datasets with item loading to the datastore L3 construct demonstrating cross module dependencies. (L2 of search being used in L3 of data store).

* Implementing auth api admin, introducing concept of sub clients and sub modules at L2 and L3 levels

* Making refactor consistently use helper functions and adding documentation to new components/API endpoints

* Adding endpoint gen from open api spec and using for auth APi

* Implementing additional L2 endpoints for auth API

* Adding comment for script

* Ignoring openapi.json

Co-authored-by: Peter Baker &lt;87056634+PeterBaker0@users.noreply.github.com&gt;

---------

Co-authored-by: Ross (Laz) Petridis &lt;Rosspet@users.noreply.github.com&gt;
Co-authored-by: Ross &lt;ross.petridis@csiro.au&gt;
Co-authored-by: Peter Baker &lt;87056634+PeterBaker0@users.noreply.github.com&gt; ([`897569c`](https://github.com/provena/provena-python-client/commit/897569c87ea786ed001d1a1869f5a865a7432a42))

* JIRA-1665 &amp; 1667 Major: Implement Auth Flow &amp; Implement Config Interface #2 (#2)

Completed base auth interface + device flow, provided more type safety to the auth device flow methods, completed config interface file with docstrings, and updated CI-CD script to only run on main.

co-authored-by: Ross &lt;ross.petridis@csiro.au&gt; ([`cb5b19b`](https://github.com/provena/provena-python-client/commit/cb5b19b5ac2fd4de6a0383d2592c29201ec6c464))


## v0.0.0 (2024-04-05)

### Unknown

* Updated semantic release build command due to some issues with containers. Not sure if its the right fix. (https://github.com/python-semantic-release/python-semantic-release/issues/723) ([`6fec972`](https://github.com/provena/provena-python-client/commit/6fec9720401a30d9f4ec0cd13b809fe293de37fd))

* JIRA-1630 Minor: Initial Stub Development for Provena Client Tool. (#1)

* Created initial package setup with cookie-cutter template

* Updated CI/CD script to only run on main branch, fixed incorrect imports and deleted files that were not needed

* Integrated mypi in the package and was able to successfully build.

* Shifted from a class to a data-class for Settings, updated CI-CD script and README.md and removed CONDUCT.md files.

* Updated CI-CD script to use OCID instead of API tokens, and made it trigger on initial branch for testing purposes.

* Simplifying CI-CD file to ensure it runs without issues.

* Removed pull-request for now from CI/CD script.

* Updated dependencies for CI

* Updated poetry lock file for CI.

* Added dummy test for CI to pass.

* Updated CI to support pull request,  as I am gonna merge pull request to main to release package.

---------

Co-authored-by: Parth-Kulkarni ([`cfab8c2`](https://github.com/provena/provena-python-client/commit/cfab8c29ea5f483eeb7032cd6ddd182f3aeff320))

* Update pull_request_template.md by removing RRAP references ([`3bd04b3`](https://github.com/provena/provena-python-client/commit/3bd04b321088401e1ecd0d2840a8779f73d221ad))

* Create pull_request_template.md ([`8666266`](https://github.com/provena/provena-python-client/commit/866626683943e8c8ba036ed933ab39c9c87b1fde))

* Initial commit ([`5cc5d2d`](https://github.com/provena/provena-python-client/commit/5cc5d2d803cd83e9445d339982ebebb1908f18d4))
