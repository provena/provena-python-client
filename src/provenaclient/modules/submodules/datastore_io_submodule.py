'''
Created Date: Tuesday June 18th 2024 +1000
Author: Peter Baker
-----
Last Modified: Tuesday June 18th 2024 12:56:41 pm +1000
Modified By: Peter Baker
-----
Description: Datastore file IO sub module, includes file upload and download helpers
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
22-08-2024 | Parth Kulkarni | Implemented method to do download specific files/directory and helper function to create S3 path.
18-06-2024 | Peter Baker | First implementation including download_all_files and upload_all_files methods
'''

from multiprocessing import Value
from pathlib import Path

from cloudpathlib import S3Path
from provenaclient.auth.manager import AuthManager
from provenaclient.utils.config import Config
from provenaclient.clients import DatastoreClient
from ProvenaInterfaces.DataStoreAPI import *
from provenaclient.modules.module_helpers import *
import cloudpathlib.s3 as s3  # type: ignore


class AccessEnum(str, Enum): 
    READ = "read"
    WRITE = "write"

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
    creds_dict = creds.credentials.dict()
    # don't want to pass expiry through as it confused s3 cloud lib
    del creds_dict['expiry']
    # create client
    client = s3.S3Client(
        **creds_dict
    )

    return client


def print_file_info(file: s3.S3Path) -> None:
    """
    Pretty prints a file specifying file/directory.
    File := s3.S3Path from Cloudpathlib

    Args:
        file (s3.S3Path): The file to print 
    """
    if file.is_dir():
        print(f"Directory: {file}")
    else:
        print(f"File: {file}")


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

    async def _create_s3_path(self, dataset_id: str, access_type: AccessEnum) -> S3Path: 
        """This helper function creates an S3 URI in PATH format by ingesting 
        the dataset id and access type (read, write). 

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to download files for - ensure you have the right access.
        access_type : AccessEnum
            The access type required (Read or Write)

        Returns
        -------
        S3Path
            S3Path instance that represent a path in S3 with filesystem path semantics.
        """

        dataset_information = await self._datastore_client.fetch_dataset(id=dataset_id)

        # Fetch the dataset information
        dataset_information = await self._datastore_client.fetch_dataset(
            id=dataset_id
        )
        # Get the S3 location
        assert dataset_information.item is not None, f"Expected non None item from dataset fetch, details: {dataset_information.status.details}."
        s3_location = dataset_information.item.s3

        if access_type == AccessEnum.READ: 
            creds = await self._datastore_client.generate_read_access_credentials(
                read_access_credentials=CredentialsRequest(
                    dataset_id=dataset_id,
                    console_session_required=False
                )
            )
        
        elif access_type == AccessEnum.WRITE: 
            creds = await self._datastore_client.generate_write_access_credentials(
                write_access_credentials=CredentialsRequest(
                    dataset_id=dataset_id,
                    console_session_required=False
                )
            )

        client = setup_s3_client(creds = creds)

        return s3.S3Path(cloud_path=s3_location.s3_uri, client=client) 

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
        
        path = await self._create_s3_path(dataset_id=dataset_id, access_type=AccessEnum.READ)

        # download to specified path
        path.download_to(destination_directory)
        # Release file handles
        path.__del__

    async def list_all_files(
        self,
        dataset_id: str,
        print_list: bool = False,
    ) -> List[s3.S3Path]:
        """
        Lists all files stored in the given dataset by ID.

        - Fetches info
        - Fetches creds
        - Uses s3 cloud path lib to list all files to specified location

        Args:
            dataset_id (str): The ID of the dataset to download files for - ensure you have read access
        """
        path = await self._create_s3_path(dataset_id=dataset_id, access_type=AccessEnum.READ)
        
        paths = []
        for path in path.glob("**/*"):
            paths.append(path)

        if print_list:
            for p in paths:
                print_file_info(p)

        # Release file handles
        path.__del__

        return paths

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
        path = await self._create_s3_path(dataset_id=dataset_id, access_type=AccessEnum.WRITE)
        # upload
        path.upload_from(source_directory)
        # Release file handles
        path.__del__

    async def download_specific_file(self, dataset_id: str, s3_file_path: str, destination_directory: str) -> None: 
        """
        Downloads a specific file or folder from an S3 bucket to a provided destination path.

        This method handles various cases:
        - If `s3_file_path` is a specific file, it downloads that file directly to `destination_directory`.
        - If `s3_file_path` is a folder (without a trailing slash), it downloads the entire folder and its contents,
        preserving the folder structure in `destination_directory`.
        - If `s3_file_path` is a folder (with a trailing slash), it downloads all contents within that folder but not the
        folder itself (unless subfolders are present, in which case those subfolders and their contents are downloaded).
        - If `s3_file_path` points to a specific nested folder (e.g., 'nested/another-nested'), it downloads only that 
        nested folder and its contents unless further specification is needed.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset that contains the files or folders to download from S3.
        s3_file_path : str
            The S3 path of the file or folder to download. 
            - If this is a specific file, it will download just that file.
            - If this is a folder without a trailing slash (e.g., 'nested'), it will download the entire folder 
            and all its contents, preserving the structure.
            - If this is a folder with a trailing slash (e.g., 'nested/'), it will download all contents within 
            that folder but not the folder itself unless subfolders are present.
            - If this points to a specific nested folder (e.g., 'nested/another-nested'), it will download only 
            that nested folder and its contents.
        destination_directory : str
            The destination path to save files to - use a directory.
            
        """

        # Generate credentials access. 
        path = await self._create_s3_path(dataset_id=dataset_id, access_type=AccessEnum.READ)

        # Now trying to download the specific file. 
        file_path = path / s3_file_path

        if not file_path.exists():
            raise FileNotFoundError(f"The specified path '{s3_file_path}' does not exist in the S3 bucket.")

        if file_path.is_file(): 
            file_path.download_to(destination_directory)

        elif file_path.is_dir() and not s3_file_path.endswith("/"):
            local_file_path = Path(destination_directory) / s3_file_path
            # This pattern finds all files and folders in the specified directory in s3 bucket.
            for item in file_path.glob("**/*"): 
                # Ensure it's a file and not a "directory" 
                if item.is_file():    
                    local_file_path = Path(destination_directory) / s3_file_path
                    # Provides permissions to create directory.
                    local_file_path.parent.mkdir(parents=True, exist_ok=True) 
                    item.download_to(local_file_path)
        else: 
            file_path.download_to(destination_directory)