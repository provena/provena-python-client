from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import DatastoreClient
from ProvenaInterfaces.DataStoreAPI import *
from provenaclient.modules.module_helpers import *
import cloudpathlib.s3 as s3  # type: ignore


def setup_s3_client(creds: CredentialResponse) -> s3.S3Client:
    """

    Uses the datastore creds response to generate an s3 cloud path lib client
    with auth.

    Args:
        creds (CredentialResponse): The data store credentials response

    Returns:
        s3.S3Client: The s3 client ready to use
    """
    # create dict of creds
    creds_dict = creds.dict()
    # don't want to pass expiry through as it confused s3 cloud lib
    del creds_dict['expiry']
    # create client
    client = s3.S3Client(
        **creds_dict
    )
    return client


class IOSubModule(ModuleService):
    _datastore_client: DatastoreClient

    def __init__(self, auth: AuthManager, config: Config, datastore_client: DatastoreClient) -> None:
        """
        File IO datastore sub module to assist with download and upload of data store files.

        Parameters
        ----------
        auth : AuthManager
            An abstract interface containing the user's requested auth flow
            method.
        config : Config
            A config object which contains information related to the Provena
            instance. 
        auth_client: AuthClient
            The instantiated auth client
        """
        self._auth = auth
        self._config = config

        # Clients related to the datastore scoped as private.
        self._datastore_client = datastore_client

    async def download_all_files(
        self,
        destination_directory: str,
        dataset_id: str
    ) -> None:
        """
        Downloads all files to the destination path for a given dataset id.

        - Fetches info
        - Fetches creds
        - Uses s3 cloud path lib to download all files to specified location

        Args:
            destination_directory (str): The destination path to save files to - use a directory
            dataset_id (str): The ID of the dataset to download files for - ensure you have read access
        """
        # Fetch the dataset information
        dataset_information = await self._datastore_client.fetch_dataset(
            id=dataset_id
        )
        # Get the S3 location
        assert dataset_information.item is not None, f"Expected non None item from dataset fetch, details: {dataset_information.status.details}."
        s3_location = dataset_information.item.s3
        # Get read credentials
        read_creds = await self._datastore_client.generate_read_access_credentials(
            read_access_credentials=CredentialsRequest(
                dataset_id=dataset_id,
                console_session_required=False
            )
        )
        # setup s3 client
        client = setup_s3_client(creds=read_creds)
        # create path
        path = s3.S3Path(cloud_path=s3_location.s3_uri, client=client)
        # download to specified path
        path.download_to(destination_directory)
        # Release file handles
        path.__del__

    async def upload_all_files(
        self,
        source_directory: str,
        dataset_id: str
    ) -> None:
        """
        Uploads all files in the source path to the specified dataset id's storage location.

        - Fetches info
        - Fetches creds
        - Uses s3 cloud path lib to upload all files to specified location

        Args:
            source_directory (str): The source path to upload files from - use a directory
            dataset_id (str): The ID of the dataset to upload files for - ensure you have write access
        """
        # Fetch the dataset information
        dataset_information = await self._datastore_client.fetch_dataset(
            id=dataset_id
        )
        # Get the S3 location
        assert dataset_information.item is not None, f"Expected non None item from dataset fetch, details: {dataset_information.status.details}."
        s3_location = dataset_information.item.s3
        # Get read credentials
        write_creds = await self._datastore_client.generate_write_access_credentials(
            write_access_credentials=CredentialsRequest(
                dataset_id=dataset_id,
                console_session_required=False
            )
        )
        # setup s3 client
        client = setup_s3_client(creds=write_creds)
        # create path
        path = s3.S3Path(cloud_path=s3_location.s3_uri, client=client)
        # upload
        path.upload_from(source_directory)
        # Release file handles
        path.__del__
