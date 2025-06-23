from google.cloud.storage import Client
from google.adk.artifacts import BaseArtifactService
import hashlib
from typing import List

class GCSArtifactService(BaseArtifactService):
    def __init__(self, bucket_name: str):
        self.client = Client()
        self.bucket = self.client.bucket(bucket_name)

    async def save_artifact(self, app_name: str, user_id: str, session_id: str, filename: str, artifact: bytes) -> str:
        version_id = hashlib.sha256(artifact).hexdigest()[:10]
        blob = self.bucket.blob(f"{app_name}/{user_id}/{session_id}/{filename}/{version_id}")
        await blob.upload_from_string(artifact)
        return version_id

    async def load_artifact(self, app_name: str, user_id: str, session_id: str, filename: str, version: str) -> bytes:
        blob = self.bucket.blob(f"{app_name}/{user_id}/{session_id}/{filename}/{version}")
        return await blob.download_as_bytes()

    async def delete_artifact(self, app_name: str, user_id: str, session_id: str, filename: str, version: str) -> None:
        blob = self.bucket.blob(f"{app_name}/{user_id}/{session_id}/{filename}/{version}")
        await blob.delete()

    async def list_artifact_keys(self, app_name: str, user_id: str, session_id: str) -> List[str]:
        prefix = f"{app_name}/{user_id}/{session_id}/"
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        keys = []
        for blob in blobs:
            # Extract filename from path like "app/user/session/filename/version"
            path_parts = blob.name[len(prefix):].split('/')
            if len(path_parts) >= 2:
                filename = path_parts[0]
                if filename not in keys:
                    keys.append(filename)
        return keys

    async def list_versions(self, app_name: str, user_id: str, session_id: str, filename: str) -> List[str]:
        prefix = f"{app_name}/{user_id}/{session_id}/{filename}/"
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        versions = []
        for blob in blobs:
            # Extract version from path like "app/user/session/filename/version"
            version = blob.name.split('/')[-1]
            versions.append(version)
        return versions

def gcs_artifact_service_builder(bucket_name: str) -> GCSArtifactService:
    return GCSArtifactService(bucket_name)
