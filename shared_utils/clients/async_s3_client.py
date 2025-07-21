from os import getenv
import aioboto3
from typing import Optional, BinaryIO, Union
import logging

class S3Client:

    def __init__(self):
        self.session = aioboto3.Session()
        
        self.region_name = getenv('AWS_S3_REGION')
        assert self.region_name, "AWS_S3_REGION environment variable must be set"

    async def upload_file(self, local_file_path: str, bucket_name: str, s3_key: str) -> bool:
        """Asynchronously uploads a file to an S3 bucket.
        Example:
            await client.upload_file('local_file.txt', 'my-bucket', 'folder/remote_file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.upload_file(local_file_path, bucket_name, s3_key)
            return True
        except Exception as e:
            logging.error(f"Upload failed: {e}")
            return False

    async def download_file(self, bucket_name: str, s3_key: str, local_file_path: str) -> bool:
        """Asynchronously downloads a file from an S3 bucket.
        Example:
            await client.download_file('my-bucket', 'folder/remote_file.txt', 'downloaded_file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.download_file(bucket_name, s3_key, local_file_path)
            return True
        except Exception as e:
            logging.error(f"Download failed: {e}")
            return False

    async def upload_fileobj(self, fileobj: BinaryIO, bucket_name: str, s3_key: str) -> bool:
        """Asynchronously uploads a file-like object to an S3 bucket.
        Example:
            with open('file.txt', 'rb') as f:
                await client.upload_fileobj(f, 'my-bucket', 'folder/remote_file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.upload_fileobj(fileobj, bucket_name, s3_key)
            return True
        except Exception as e:
            logging.error(f"Upload fileobj failed: {e}")
            return False

    async def download_fileobj(self, bucket_name: str, s3_key: str, fileobj: BinaryIO) -> bool:
        """Asynchronously downloads a file from S3 to a file-like object.
        Example:
            with open('downloaded_file.txt', 'wb') as f:
                await client.download_fileobj('my-bucket', 'folder/remote_file.txt', f)
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.download_fileobj(bucket_name, s3_key, fileobj)
            return True
        except Exception as e:
            logging.error(f"Download fileobj failed: {e}")
            return False

    async def put_object(self, bucket_name: str, s3_key: str, body: Union[str, bytes]) -> bool:
        """Asynchronously uploads data directly to S3.
        Example:
            await client.put_object('my-bucket', 'data.json', json.dumps(data))
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.put_object(Bucket=bucket_name, Key=s3_key, Body=body)
            return True
        except Exception as e:
            logging.error(f"Put object failed: {e}")
            return False

    async def get_object(self, bucket_name: str, s3_key: str) -> Optional[bytes]:
        """Asynchronously retrieves an object from S3.
        Example:
            data = await client.get_object('my-bucket', 'data.json')
            if data:
                content = json.loads(data.decode('utf-8'))
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                response = await s3.get_object(Bucket=bucket_name, Key=s3_key)
                return await response['Body'].read()
        except Exception as e:
            logging.error(f"Get object failed: {e}")
            return None

    async def delete_object(self, bucket_name: str, s3_key: str) -> bool:
        """Asynchronously deletes an object from S3.
        Example:
            await client.delete_object('my-bucket', 'old_file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.delete_object(Bucket=bucket_name, Key=s3_key)
            return True
        except Exception as e:
            logging.error(f"Delete object failed: {e}")
            return False

    async def list_objects(self, bucket_name: str, prefix: str = '') -> list[dict]:
        """Asynchronously lists objects in an S3 bucket with optional prefix.
        Example:
            objects = await client.list_objects('my-bucket', 'folder/')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                response = await s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
                return response.get('Contents', [])
        except Exception as e:
            logging.error(f"List objects failed: {e}")
            return []

    async def object_exists(self, bucket_name: str, s3_key: str) -> bool:
        """Asynchronously checks if an object exists in S3.
        Example:
            exists = await client.object_exists('my-bucket', 'file.txt')
        """
        try:
            async with self.session.client('s3', region_name=self.region_name) as s3:
                await s3.head_object(Bucket=bucket_name, Key=s3_key)
            return True
        except Exception:
            return False


async_s3_client = S3Client()  # module level singleton instance
