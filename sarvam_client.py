import asyncio
import aiofiles
from urllib.parse import urlparse
from azure.storage.filedatalake.aio import DataLakeDirectoryClient, FileSystemClient
from azure.storage.filedatalake import ContentSettings
import mimetypes
import logging
from pprint import pprint
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()

# Configuration
API_SUBSCRIPTION_KEY = os.getenv("SARVAM_KEY")
LANGUAGE_CODE = "ta-IN" 

class SarvamClient:
    def __init__(self, url: str):
        self.account_url, self.file_system_name, self.directory_name, self.sas_token = (
            self._extract_url_components(url)
        )
        self.lock = asyncio.Lock()
        print(f"Initialized SarvamClient with directory: {self.directory_name}")

    def update_url(self, url: str):
        self.account_url, self.file_system_name, self.directory_name, self.sas_token = (
            self._extract_url_components(url)
        )
        print(f"Updated URL to directory: {self.directory_name}")

    def _extract_url_components(self, url: str):
        parsed_url = urlparse(url)
        account_url = f"{parsed_url.scheme}://{parsed_url.netloc}".replace(
            ".blob.", ".dfs."
        )
        path_components = parsed_url.path.strip("/").split("/")
        file_system_name = path_components[0]
        directory_name = "/".join(path_components[1:])
        sas_token = parsed_url.query
        return account_url, file_system_name, directory_name, sas_token

    async def upload_files(self, local_file_paths, overwrite=True):
        print(f"Starting upload of {len(local_file_paths)} files")
        async with DataLakeDirectoryClient(
            account_url=f"{self.account_url}?{self.sas_token}",
            file_system_name=self.file_system_name,
            directory_name=self.directory_name,
            credential=None,
        ) as directory_client:
            tasks = []
            for path in local_file_paths:
                file_name = path.split("\\")[-1]
                print(f'file name: {file_name}')
                tasks.append(
                    self._upload_file(directory_client, path, file_name, overwrite)
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print(
                f"Upload completed for {sum(1 for r in results if not isinstance(r, Exception))} files"
            )

    async def _upload_file(
        self, directory_client, local_file_path, file_name, overwrite=True
    ):
        try:
            async with aiofiles.open(local_file_path, mode="rb") as file_data:
                mime_type = mimetypes.guess_type(local_file_path)[0] or 'audio/wav'
                file_client = directory_client.get_file_client(file_name)
                data = await file_data.read()
                await file_client.upload_data(
                    data,
                    overwrite=overwrite,
                    content_settings=ContentSettings(content_type=mime_type),
                )
                print(f"✅ File uploaded successfully: {file_name}")
                print(f"   Type: {mime_type}")
                return True
        except Exception as e:
            print(f"❌ Upload failed for {file_name}: {str(e)}")
            return False

    async def list_files(self):
        print("\n📂 Listing files in directory...")
        file_names = []
        async with FileSystemClient(
            account_url=f"{self.account_url}?{self.sas_token}",
            file_system_name=self.file_system_name,
            credential=None,
        ) as file_system_client:
            async for path in file_system_client.get_paths(self.directory_name):
                file_name = path.name.split("/")[-1]
                async with self.lock:
                    file_names.append(file_name)
        print(f"Found {len(file_names)} files:")
        for file in file_names:
            print(f"   📄 {file}")
        return file_names

    async def download_files(self, file_names, destination_dir):
        print(f"\n⬇️ Starting download of {len(file_names)} files to {destination_dir}")
        async with DataLakeDirectoryClient(
            account_url=f"{self.account_url}?{self.sas_token}",
            file_system_name=self.file_system_name,
            directory_name=self.directory_name,
            credential=None,
        ) as directory_client:
            tasks = []
            for file_name in file_names:
                tasks.append(
                    self._download_file(directory_client, file_name, destination_dir)
                )
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print(
                f"Download completed for {sum(1 for r in results if not isinstance(r, Exception))} files"
            )

    async def _download_file(self, directory_client, file_name, destination_dir):
        try:
            file_client = directory_client.get_file_client(file_name)
            download_path = f"{destination_dir}/{file_name}"
            async with aiofiles.open(download_path, mode="wb") as file_data:
                stream = await file_client.download_file()
                data = await stream.readall()
                await file_data.write(data)
            print(f"✅ Downloaded: {file_name} -> {download_path}")
            return True
        except Exception as e:
            print(f"❌ Download failed for {file_name}: {str(e)}")
            return False