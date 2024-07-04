# CHANGELOG

## v0.10.2 (2024-07-04)

### Fix

* fix: forcing rebuild due to trusted publisher issue ([`7136675`](https://github.com/provena/provena-python-client/commit/7136675eab81168ba74f8bc7a1caeb847dd4911f))

### Unknown

* Merge branch &#39;main&#39; of github.com:provena/provena-python-client into main ([`bda5606`](https://github.com/provena/provena-python-client/commit/bda5606d3a6d083c2d31e1f6e7e06d5095c0a3db))

## v0.10.1 (2024-07-04)

### Ci

* ci: Fixing missing fetch depth = 0 and documenting ([`2302b7a`](https://github.com/provena/provena-python-client/commit/2302b7a7370fbcbdc1d72ac9164286dc2d5cb5f3))

* ci: Fixing missing pass through for CD action (#22) ([`0896a36`](https://github.com/provena/provena-python-client/commit/0896a3645f44634c53f340bbfc91387c35a29b5f))

* ci: Modularisation of CI/CD into actions to clearly separate trigger files (#21) ([`e1f4664`](https://github.com/provena/provena-python-client/commit/e1f46640b600d8388fcba6be6b6d42ab886ea0bd))

### Fix

* fix: Adding more py.typed markers ([`ff3e029`](https://github.com/provena/provena-python-client/commit/ff3e02983637ba2c2343c039412b0347b1523e02))

### Unknown

* Merge branches &#39;modular-actions-setup&#39; and &#39;main&#39; of github.com:provena/provena-python-client into main ([`fee9615`](https://github.com/provena/provena-python-client/commit/fee96152cc82198c6934387d6f86fcf8a665c511))

* Fixing not using new input ([`45cc98c`](https://github.com/provena/provena-python-client/commit/45cc98c7c436dc7e0d10cdd540ae5f1ee74eec54))

* Merge branch &#39;main&#39; into modular-actions-setup ([`36bfd12`](https://github.com/provena/provena-python-client/commit/36bfd128d936a77961008e16da106598845951ae))

* Pass through GITHUB_TOKEN from parent workflow ([`296eba3`](https://github.com/provena/provena-python-client/commit/296eba3e0c5d1cdbe9ffd22d439992aba501ba14))

* Removing test file ([`eae09bf`](https://github.com/provena/provena-python-client/commit/eae09bf37c19ee6bb6faeedc4d5acd7090497ba3))

* Removing fetch depth zero to be safe ([`88fcdba`](https://github.com/provena/provena-python-client/commit/88fcdbaf2f926941fed5425da9aa581e18f2f739))

* Cloning repo before all actions ([`69f2309`](https://github.com/provena/provena-python-client/commit/69f23094a16afa960f2b5d4f5d90438923b43a90))

* Update including test ([`e16f672`](https://github.com/provena/provena-python-client/commit/e16f6728171520dd9e73a231bebcb332e1c58a95))

* fix:Update auth&#39;s __init__.py (#20) ([`b555bd1`](https://github.com/provena/provena-python-client/commit/b555bd1bfea9a48eb302ab4c839950dc0feac9be))

## v0.10.0 (2024-07-02)

### Feature

* feat: improving dependency resolution and adding interfaces (#19) ([`d941a8c`](https://github.com/provena/provena-python-client/commit/d941a8cdb5031bbb9d634ec9ee8d58a6681660b2))

## v0.9.0 (2024-06-28)

### Documentation

* docs: Completed Release Process Documentation. (#17) ([`2c8f20f`](https://github.com/provena/provena-python-client/commit/2c8f20fd45137be6f1b483a72a5e18ff542e0429))

### Feature

* feat: JIRA-1710 (minor) completing registry api L2 and L3 interfaces with support for admin, general and other endpoints.  (#18) ([`cd2b4e9`](https://github.com/provena/provena-python-client/commit/cd2b4e9b37f1c1359694014854cde47121ee5ff8))

## v0.8.0 (2024-06-21)

### Feature

* feat: Updated pyproject.toml settings to increment project versioning. ([`b61fe49`](https://github.com/provena/provena-python-client/commit/b61fe49c598052863a6ea6f7ab472301b6d04035))

* feat: changed semantic release settings to increment project version. ([`1899df9`](https://github.com/provena/provena-python-client/commit/1899df90d798765ec4082e1eccf93c24960ce23a))

### Unknown

* Merge branch &#39;main&#39; of github.com:provena/provena-python-client into main ([`cd6ad90`](https://github.com/provena/provena-python-client/commit/cd6ad90cafdc39242540e5a55b1bfdffa40332e8))

## v0.7.0 (2024-06-21)

### Feature

* feat: Testing version increment. ([`bff0daf`](https://github.com/provena/provena-python-client/commit/bff0daf3ceef3d7af025ba187cc96601942ce9eb))

### Unknown

* Included pytest-asycnio missing dependency. ([`8d4442a`](https://github.com/provena/provena-python-client/commit/8d4442a46a358efe1bc01eebdbcda00ed297b51f))

* Completed Unit Testing for L1 &amp; L2 Layers.

* Completed L1 layer testing mocked with various http methods and status codes.

* Completed L1 layer testing, created fixtures and also added small set of integration tests for L1 layer.

* Completed L2 Layer Testing, need further review on missing tests and what can be improved.

* Fixed some tests that were failing due to wrong HTTP type or incorrect use of final url.

* Completed unit tests with doc string and exception chain identification.

* Updated CI-CD script to run only once.

* Added header commenting to files.

* Updated lock file.

* mypy testing. Does not seem to be an issue on my end.

* Included pytest-httpx dependency.

* change mocked auth service to use  base class methods only and updated robustness of exception chaining function. ([`8c52602`](https://github.com/provena/provena-python-client/commit/8c52602482c15eb71f694a90172b5ac0c2538498))

* Refactoring auth interface (#13)

Small refactor of config instantiation ([`7d6dea5`](https://github.com/provena/provena-python-client/commit/7d6dea55a6a80bff49774f0e7bd9e967d36d4dc7))

## v0.6.0 (2024-06-18)

### Feature

* feat: forcing update to 0.6.0 ([`91e2879`](https://github.com/provena/provena-python-client/commit/91e2879c45dc35fcb6c97e467de8133f6dfee4cc))

### Unknown

* Adding dataset L3 level IO functions + class header files (#14)

* Download method completed in sub module to isolate s3 functionality - added sub module sub folder

* Implementing the upload method and improving variable names

* Adding file header and configuration for the psioniq extensions

* Class header documentation and other clean up

* Fixing lock files

* Adding list all files ([`b7a4388`](https://github.com/provena/provena-python-client/commit/b7a438839a7f2987f8fa3ce79ae89b29154bc66c))

## v0.5.0 (2024-06-18)

### Feature

* feat: forcing another attempt ([`5bb0e49`](https://github.com/provena/provena-python-client/commit/5bb0e49235992bbe8d46d48c4b58dd7c99564826))

## v0.4.0 (2024-06-18)

### Feature

* feat: Updating pyproject to promote new release ([`34b71da`](https://github.com/provena/provena-python-client/commit/34b71dad6235781294787b4325c9c10891c62b8b))

### Unknown

* Trigger another build ([`12205b4`](https://github.com/provena/provena-python-client/commit/12205b47ca15b6ed266dab5d63e6ed0d90aa8b0b))

## v0.3.0 (2024-06-17)

### Feature

* feat(major): First major release ([`30ac329`](https://github.com/provena/provena-python-client/commit/30ac329ed30a88c397ff98b31b4d24198ddee585))

### Unknown

* Removing union pipes (#12) ([`ea83080`](https://github.com/provena/provena-python-client/commit/ea83080307a9a7c601670f56f67c7c4a3d3b202f))

* Jira-1670(Minor): Offline token auth flow  (#11)

Implements offline token authentication method ([`0a6f0b3`](https://github.com/provena/provena-python-client/commit/0a6f0b32709231dfa2c6a4e1741f9b4fea1807c3))

* JIRA 1692 - Completion of Prov API functionalities for Client Library.  (#9)

* completed explore endpoints as a concept, and now working on the model run endpoint.

* Completed prov-api L2 methods and setup of L3 methods.

* Completed documentation and working on building the Admin Client of Prov-API.

* commiting current changes, currently working on admin endpoints.

* Completion of Prov-API, completed all documentation and remaining admin and CSV related endpoints.

* Fixed missing parameters in two of the admin methods. One of the admin endpoints needs to be tested.

* Completed Prov API with testing and improved the L2 and L3 layer exchange of the csv to model run method.

* Completed pull request comments and updated open api endpoints fetch script through GPT.

* Updated file  writing functions according to pull request comments and created more flexibility between L2 and L3 for launching model runs endpoint.

* Made writing file logic more robust by having more checks and throwing exceptions accordingly. Updated L2 method to encode string to bytes internally. ([`ccdcdaa`](https://github.com/provena/provena-python-client/commit/ccdcdaaee2ef64381ec66125ac65b7d421d8813b))

* Revert &#34;refactoring&#34;

This reverts commit b4f13026a3a93ef22843fc52487c10cbaacb4812. ([`0c39cee`](https://github.com/provena/provena-python-client/commit/0c39cee8f414c6d95ce2e1a03f6f9f7959a6e536))

* Revert &#34;added read offline token from file. Need to consolidate offline and refreh token mishaps&#34;

This reverts commit 0eb280a96a2f2935751cfa1a3be02d35a79879ec. ([`999a812`](https://github.com/provena/provena-python-client/commit/999a8124b8a3b06395c03ad8545b598b48c7362b))

* Revert &#34;improved error handling and tidying&#34;

This reverts commit b5a679ab36a23dd9e1cb2c655775fbe234068c76. ([`186ec49`](https://github.com/provena/provena-python-client/commit/186ec49201efb527477b2285e2caade9ca9bfece))

* git pushMerge branch &#39;main&#39; of github.com:provena/provena-python-client into main ([`e333078`](https://github.com/provena/provena-python-client/commit/e333078e9f86d7bddf067b4537fb121f6ca5595e))

* improved error handling and tidying ([`b5a679a`](https://github.com/provena/provena-python-client/commit/b5a679ab36a23dd9e1cb2c655775fbe234068c76))

* Implements Job API L2 and L3 + additional L3 helper methods (#10)

* Basic L2/L3 complete

* Building out L3 functions to await completion of job lifecycle + list all + for all methods. ([`0871e96`](https://github.com/provena/provena-python-client/commit/0871e96944be0f9b26e9ab167e1a050a2c80bd65))

* added read offline token from file. Need to consolidate offline and refreh token mishaps ([`0eb280a`](https://github.com/provena/provena-python-client/commit/0eb280a96a2f2935751cfa1a3be02d35a79879ec))

* refactoring ([`b4f1302`](https://github.com/provena/provena-python-client/commit/b4f13026a3a93ef22843fc52487c10cbaacb4812))

* Completion of Datastore Functionality (Need Review on Pagination Implementation)  (#8)

* In progressing completing of the datastore api&#39;s.

* (In progress) Completing the datastore client library functionality.

* Completion of core datastore functionalities, and need a review on pagination implementation.

* Updated pull request comments, implemented new pagination methods and removed api_exceptions list as they all inherit from BaseException.

* Completion - Improved variable naming, changed structure of listing dataset methods to be flat and not nested and removed default sort options as this is handled by the API. ([`b9e976d`](https://github.com/provena/provena-python-client/commit/b9e976dd61fcc934fa0c3945e67c24c0212e133a))

* Registry concept (#7)

* Proof of concept for registry implementation

* Adding documentation and mvp for registry implementation - not complete ([`7da100e`](https://github.com/provena/provena-python-client/commit/7da100ee6772bfe4b876112521316a187753c436))

* JIRA 1687 - Fleshing out base structure of Prov, Registry, Job and Handle ID API&#39;s (#6)

* Completed a base setup for the remaining API&#39;s (registry,prov) in respect to L2 and L3 and included all endpoints.

* Completion of missing API implementation and used a more robust approach suggested by Ross for Registry Endpoint collection.

* Changed handle to ID and implemented auto-generated routes for registry.

* Implementing L2 and L3 for ID service, renaming client file.

---------

Co-authored-by: Peter Baker &lt;peter.baker122@csiro.au&gt; ([`831e80b`](https://github.com/provena/provena-python-client/commit/831e80be517154dfa239e773c41c73f4813264ad))

* Complete L2 &amp; L3 for Auth API (#5)

* Implementing remaining L2 methods for auth api client

* Direct map L3 methods

* Adding placeholder L3 module for streamlining user links and adding doc strings for L2 auth API.

* Transferring doc strings from L2 to L3 to match - auto docs need to pick these up

* Minor corrections ([`26afd0a`](https://github.com/provena/provena-python-client/commit/26afd0a066dd66b2362687e5ce4e22ae473143a1))

## v0.2.0 (2024-05-30)

### Feature

* feat: Updated the project version to not clash with pypi. ([`e67d002`](https://github.com/provena/provena-python-client/commit/e67d002b00003f9a4be402ec7a5fd461fb0c2a48))

* feat: Updated project version to not clash with pypi. ([`a02a0b1`](https://github.com/provena/provena-python-client/commit/a02a0b181e744ff877e113e3fa9954b5e31cc2fe))

### Unknown

* Merge branch &#39;main&#39; of github.com:provena/provena-python-client into main ([`293cf17`](https://github.com/provena/provena-python-client/commit/293cf179aa50c39e5341b379c822672f913a6882))

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
