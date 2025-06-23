from google import genai
from google.genai import types
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests
import base64
import uuid
import os
from google.adk.tools.tool_context import ToolContext
from datetime import datetime
from dotenv import load_dotenv

# Imports pour Imagen
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

load_dotenv()
GCS_BUCKET_NAME = "facebook-agent"
bucket = f'{GCS_BUCKET_NAME}'

# Initialisation Vertex AI pour Imagen
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "facebook-agent-461716"), 
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

# Model Imagen
generation_model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-05-20")

from google.cloud import storage

def upload_image_to_gcs(image_path: str, bucket_name: str, destination_blob_name: str = None) -> str:
    """
    Upload an image to Google Cloud Storage and return the public URL.
    :param image_path: Local path to the image.
    :param bucket_name: GCS bucket name.
    :param destination_blob_name: File name in GCS (optional).
    :return: Public URL of the image.
    """
    today = datetime.now().strftime("%Y/%m/%d")
    if destination_blob_name is None:
        destination_blob_name = os.path.basename(image_path)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload du fichier
    blob.upload_from_filename(image_path)

    return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"

def upload_image_to_gcs_from_bytes(image_data: bytes, bucket_name: str, user_id: str = None) -> str:
    """
    Direct upload with organized folder structure.
    """
    today = datetime.now().strftime("%Y/%m/%d")
    image_filename = f"{uuid.uuid4().hex}.png"
    
    if user_id:
        destination_path = f"users/{user_id}/images/{today}/{image_filename}"
    else:
        destination_path = f"generated_images/{today}/{image_filename}"
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_path)
    
    blob.upload_from_string(image_data, content_type='image/png')
    
    return f"https://storage.googleapis.com/{bucket_name}/{destination_path}"

def upload_vertex_image_to_gcs(vertex_image, bucket_name: str, user_id: str = None) -> str:
    """
    Upload a Vertex AI image to GCS by first converting to bytes.
    """
    # Convertir l'image Vertex AI en bytes
    pil_image = vertex_image._pil_image
    image_bytes = BytesIO()
    pil_image.save(image_bytes, format='PNG')
    image_data = image_bytes.getvalue()
    
    return upload_image_to_gcs_from_bytes(image_data, bucket_name, user_id)

def generate_image_from_prompt(
    prompt: str, 
    tool_context: ToolContext,
    bucket_name: str = bucket,
    number_of_images: int = 1,
    aspect_ratio: str = "1:1",
    negative_prompt: str = ""
) -> str:
    """
    Generates an image with Imagen and uploads it directly to GCS with an organized structure.
    Returns the URL of the first generated image.
    """
    # Récupérer le user_id depuis le ToolContext
    user_id = tool_context.state.get("user_id", "anonymous")
    
    images = generation_model.generate_images(
        prompt=prompt,
        number_of_images=number_of_images,
        aspect_ratio="1:1",
        negative_prompt=negative_prompt,
        person_generation="",
        safety_filter_level="",
        add_watermark=True,
    )
    
    if images:
        # Upload la première image et retourner son URL
        public_url = upload_vertex_image_to_gcs(images[0], bucket_name, user_id)
        return public_url
    
    return None

def generate_multiple_images_from_prompt(
    prompt: str, 
    tool_context: ToolContext,
    bucket_name: str = bucket,
    number_of_images: int = 4,
    aspect_ratio: str = "1:1",
    negative_prompt: str = ""
) -> list:
    """
    Generates multiple images with Imagen and uploads all to GCS.
    Returns a list of URLs.
    """
    # Récupérer le user_id depuis le ToolContext
    user_id = tool_context.state.get("user_id", "anonymous")
    
    images = generation_model.generate_images(
        prompt=prompt,
        number_of_images=number_of_images,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
        person_generation="",
        safety_filter_level="",
        add_watermark=True,
    )
    
    urls = []
    for image in images:
        public_url = upload_vertex_image_to_gcs(image, bucket_name, user_id)
        urls.append(public_url)
    
    return urls

def generate_promotion_flyer(
    product_name: str,
    price: str,
    tool_context: ToolContext,
    currency: str = "francs CFA",
    bucket_name: str = bucket
) -> str:
    """
    Generates a promotion flyer with Imagen.
    """
    prompt = f"a promotion flyer for a {product_name} the price is {price} {currency}"
    
    return generate_image_from_prompt(
        prompt=prompt,
        tool_context=tool_context,
        bucket_name=bucket_name,
        aspect_ratio="1:1"
    )

def generate_social_media_post_image(
    content_description: str,
    tool_context: ToolContext,
    style: str = "modern and attractive",
    bucket_name: str = bucket,
    aspect_ratio: str = "1:1"
) -> str:
    """
    Generates an image for a social media post.
    """
    prompt = f"Image for social media post: {content_description}, style {style}"
    
    return generate_image_from_prompt(
        prompt=prompt,
        tool_context=tool_context,
        bucket_name=bucket_name,
        aspect_ratio=aspect_ratio
    )