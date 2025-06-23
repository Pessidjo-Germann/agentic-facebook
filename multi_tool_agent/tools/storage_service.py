# services/storage_service.py

from google.cloud import storage
import os

# Initialise Cloud Storage
bucket_name = os.getenv("GCS_BUCKET_NAME")  # Ex: "facebook-manager-assets"
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def upload_image(file_path: str, destination_blob_name: str) -> str:
    """Uploads a local image to Cloud Storage and returns its public URL.

    args:
        file_path (str): The local file path of the image to upload.
        destination_blob_name (str): The desired name for the file in the Cloud Storage bucket.

    returns:
        str: The public URL of the uploaded image.

    examples:
        >>> upload_image("/path/to/local/image.jpg", "images/uploaded_image.jpg")
        'https://storage.googleapis.com/your-bucket-name/images/uploaded_image.jpg'

    """
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    blob.make_public()  # Makes the file publicly accessible
    return blob.public_url

def upload_image_from_bytes(image_bytes: bytes, destination_blob_name: str) -> str:
    """Uploads an image from bytes in memory to Cloud Storage and returns its public URL.

    args:
        image_bytes (bytes): The binary data of the image to upload.
        destination_blob_name (str): The desired name for the file in the Cloud Storage bucket.

    returns:
        str: The public URL of the uploaded image.

    examples:
        >>> with open("/path/to/local/image.png", "rb") as f:
        ...     img_bytes = f.read()
        >>> upload_image_from_bytes(img_bytes, "images/uploaded_image.png")
        'https://storage.googleapis.com/your-bucket-name/images/uploaded_image.png'

    """
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(image_bytes, content_type='image/jpeg')  # Or 'image/png' depending on your files
    blob.make_public()
    return blob.public_url
