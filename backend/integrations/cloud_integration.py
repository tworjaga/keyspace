"""
Cloud Integration
Provides cloud storage integration for wordlists and results
"""

import os
import logging
import time
from pathlib import Path
from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CloudProvider(ABC):
    """Abstract base class for cloud providers"""

    def __init__(self, bucket: str, access_key: str, secret_key: str):
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

    @abstractmethod
    def upload_file(self, local_path: str, remote_name: str) -> bool:
        """Upload file to cloud storage"""
        pass

    @abstractmethod
    def download_file(self, remote_name: str, local_path: str) -> bool:
        """Download file from cloud storage"""
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in cloud storage"""
        pass

    @abstractmethod
    def delete_file(self, remote_name: str) -> bool:
        """Delete file from cloud storage"""
        pass


class AWSProvider(CloudProvider):
    """AWS S3 integration"""

    def __init__(self, bucket: str, access_key: str, secret_key: str, region: str = "us-east-1"):
        super().__init__(bucket, access_key, secret_key)
        self.region = region
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize AWS S3 client"""
        try:
            import boto3
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            logger.info("AWS S3 client initialized")
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
        except Exception as e:
            logger.error(f"AWS client initialization failed: {e}")

    def upload_file(self, local_path: str, remote_name: str) -> bool:
        if not self.client:
            return False

        try:
            self.client.upload_file(local_path, self.bucket, remote_name)
            logger.info(f"Uploaded {local_path} to s3://{self.bucket}/{remote_name}")
            return True
        except Exception as e:
            logger.error(f"AWS upload failed: {e}")
            return False

    def download_file(self, remote_name: str, local_path: str) -> bool:
        if not self.client:
            return False

        try:
            self.client.download_file(self.bucket, remote_name, local_path)
            logger.info(f"Downloaded s3://{self.bucket}/{remote_name} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"AWS download failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        if not self.client:
            return []

        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            return files
        except Exception as e:
            logger.error(f"AWS list failed: {e}")
            return []

    def delete_file(self, remote_name: str) -> bool:
        if not self.client:
            return False

        try:
            self.client.delete_object(Bucket=self.bucket, Key=remote_name)
            logger.info(f"Deleted s3://{self.bucket}/{remote_name}")
            return True
        except Exception as e:
            logger.error(f"AWS delete failed: {e}")
            return False


class GCPProvider(CloudProvider):
    """Google Cloud Storage integration"""

    def __init__(self, bucket: str, access_key: str, secret_key: str):
        super().__init__(bucket, access_key, secret_key)
        self.client = None
        self.bucket_obj = None
        self._init_client()

    def _init_client(self):
        """Initialize GCP client"""
        try:
            from google.cloud import storage
            import google.auth

            # For simplicity, using service account key
            # In production, use proper authentication
            self.client = storage.Client()
            self.bucket_obj = self.client.bucket(self.bucket)
            logger.info("GCP Storage client initialized")
        except ImportError:
            logger.error("google-cloud-storage not installed. Install with: pip install google-cloud-storage")
        except Exception as e:
            logger.error(f"GCP client initialization failed: {e}")

    def upload_file(self, local_path: str, remote_name: str) -> bool:
        if not self.bucket_obj:
            return False

        try:
            blob = self.bucket_obj.blob(remote_name)
            blob.upload_from_filename(local_path)
            logger.info(f"Uploaded {local_path} to gs://{self.bucket}/{remote_name}")
            return True
        except Exception as e:
            logger.error(f"GCP upload failed: {e}")
            return False

    def download_file(self, remote_name: str, local_path: str) -> bool:
        if not self.bucket_obj:
            return False

        try:
            blob = self.bucket_obj.blob(remote_name)
            blob.download_to_filename(local_path)
            logger.info(f"Downloaded gs://{self.bucket}/{remote_name} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"GCP download failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        if not self.bucket_obj:
            return []

        try:
            blobs = self.bucket_obj.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"GCP list failed: {e}")
            return []

    def delete_file(self, remote_name: str) -> bool:
        if not self.bucket_obj:
            return False

        try:
            blob = self.bucket_obj.blob(remote_name)
            blob.delete()
            logger.info(f"Deleted gs://{self.bucket}/{remote_name}")
            return True
        except Exception as e:
            logger.error(f"GCP delete failed: {e}")
            return False


class AzureProvider(CloudProvider):
    """Azure Blob Storage integration"""

    def __init__(self, bucket: str, access_key: str, secret_key: str):
        super().__init__(bucket, access_key, secret_key)
        self.client = None
        self.container_client = None
        self._init_client()

    def _init_client(self):
        """Initialize Azure client"""
        try:
            from azure.storage.blob import BlobServiceClient

            account_url = f"https://{self.access_key}.blob.core.windows.net"
            self.client = BlobServiceClient(account_url=account_url, credential=self.secret_key)
            self.container_client = self.client.get_container_client(self.bucket)
            logger.info("Azure Blob Storage client initialized")
        except ImportError:
            logger.error("azure-storage-blob not installed. Install with: pip install azure-storage-blob")
        except Exception as e:
            logger.error(f"Azure client initialization failed: {e}")

    def upload_file(self, local_path: str, remote_name: str) -> bool:
        if not self.container_client:
            return False

        try:
            with open(local_path, 'rb') as data:
                self.container_client.upload_blob(name=remote_name, data=data, overwrite=True)
            logger.info(f"Uploaded {local_path} to Azure container {self.bucket}/{remote_name}")
            return True
        except Exception as e:
            logger.error(f"Azure upload failed: {e}")
            return False

    def download_file(self, remote_name: str, local_path: str) -> bool:
        if not self.container_client:
            return False

        try:
            with open(local_path, 'wb') as download_file:
                download_stream = self.container_client.download_blob(remote_name)
                download_file.write(download_stream.readall())
            logger.info(f"Downloaded Azure {self.bucket}/{remote_name} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Azure download failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        if not self.container_client:
            return []

        try:
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Azure list failed: {e}")
            return []

    def delete_file(self, remote_name: str) -> bool:
        if not self.container_client:
            return False

        try:
            self.container_client.delete_blob(remote_name)
            logger.info(f"Deleted Azure {self.bucket}/{remote_name}")
            return True
        except Exception as e:
            logger.error(f"Azure delete failed: {e}")
            return False


class CloudIntegration:
    """Main cloud integration class"""

    def __init__(self, provider: str = "aws", bucket: str = "",
                 access_key: str = "", secret_key: str = ""):
        self.provider_name = provider.lower()
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.provider = None

        self._init_provider()

    def _init_provider(self):
        """Initialize the appropriate cloud provider"""
        try:
            if self.provider_name == "aws":
                self.provider = AWSProvider(self.bucket, self.access_key, self.secret_key)
            elif self.provider_name == "gcp":
                self.provider = GCPProvider(self.bucket, self.access_key, self.secret_key)
            elif self.provider_name == "azure":
                self.provider = AzureProvider(self.bucket, self.access_key, self.secret_key)
            else:
                logger.error(f"Unsupported cloud provider: {self.provider_name}")

            if self.provider:
                logger.info(f"Cloud integration initialized with {self.provider_name}")

        except Exception as e:
            logger.error(f"Cloud provider initialization failed: {e}")

    def upload_file(self, local_path: str, remote_name: str) -> bool:
        """Upload file to cloud storage"""
        if not self.provider:
            logger.error("Cloud provider not initialized")
            return False

        return self.provider.upload_file(local_path, remote_name)

    def download_file(self, remote_name: str, local_path: str) -> bool:
        """Download file from cloud storage"""
        if not self.provider:
            logger.error("Cloud provider not initialized")
            return False

        return self.provider.download_file(remote_name, local_path)

    def list_files(self, prefix: str = "") -> List[str]:
        """List files in cloud storage"""
        if not self.provider:
            logger.error("Cloud provider not initialized")
            return []

        return self.provider.list_files(prefix)

    def delete_file(self, remote_name: str) -> bool:
        """Delete file from cloud storage"""
        if not self.provider:
            logger.error("Cloud provider not initialized")
            return False

        return self.provider.delete_file(remote_name)

    def sync_wordlist(self, local_path: str, remote_name: str, direction: str = "upload") -> bool:
        """
        Sync wordlist between local and cloud

        Args:
            local_path: Local file path
            remote_name: Remote file name
            direction: "upload" or "download"
        """
        if direction == "upload":
            return self.upload_file(local_path, remote_name)
        elif direction == "download":
            return self.download_file(remote_name, local_path)
        else:
            logger.error(f"Invalid sync direction: {direction}")
            return False

    def backup_results(self, results_file: str, backup_name: str = None) -> bool:
        """Backup results to cloud storage"""
        if not backup_name:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_results_{timestamp}.json"

        return self.upload_file(results_file, f"backups/{backup_name}")

    def get_storage_info(self) -> Dict[str, Any]:
        """Get cloud storage information"""
        if not self.provider:
            return {"error": "Cloud provider not initialized"}

        try:
            files = self.list_files()
            return {
                "provider": self.provider_name,
                "bucket": self.bucket,
                "file_count": len(files),
                "files": files[:10],  # First 10 files
                "total_files_available": len(files)
            }
        except Exception as e:
            return {"error": str(e)}
