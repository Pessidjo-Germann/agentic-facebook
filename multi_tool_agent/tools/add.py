from google.cloud import storage
GCS_BUCKET_NAME = "facebook-agent"
bucket = {GCS_BUCKET_NAME}
def check_bucket_exists(bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        raise Exception(f"Bucket '{bucket_name}' does not exist.")

check_bucket_exists(bucket)
