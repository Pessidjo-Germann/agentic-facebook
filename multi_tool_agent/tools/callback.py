import base64
import os
import uuid
from datetime import datetime
from typing import Dict, Optional

from google.cloud import storage
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

# GCS bucket configuration
GCS_BUCKET_NAME = "facebook-agent"  # Replace with your bucket name

def upload_user_image_to_gcs(image_data: bytes, mime_type: str, user_id: str = None, image_count: int = 1) -> str:
    """
    Uploads a user image to GCS with an organized structure.
    
    Args:
        image_data: Image bytes
        mime_type: MIME type of the image
        user_id: User ID (optional)
        image_count: Image number in the session
    
    Returns:
        str: Public URL of the uploaded image
    """
    # Get extension from MIME type
    extension = mime_type.split("/")[-1]
    if extension == "jpeg":
        extension = "jpg"
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"user_asset_{image_count}_{timestamp}_{uuid.uuid4().hex[:8]}.{extension}"
    
    # Create folder structure
    today = datetime.now().strftime("%Y/%m/%d")
    if user_id:
        destination_path = f"users/{user_id}/uploaded_images/{today}/{image_filename}"
    else:
        destination_path = f"user_uploads/{today}/{image_filename}"
    
    try:
        # Upload to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(destination_path)
        
        blob.upload_from_string(image_data, content_type=mime_type)
        
        # Return public URL
        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{destination_path}"
        print(f"[Image Callback] Image uploaded to GCS: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"[Image Callback] Error uploading to GCS: {str(e)}")
        return None

def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Callback that executes before the model is called.
    Detects and uploads inline images from user messages to Google Cloud Storage
    for use by the agents.

    Args:
        callback_context: The callback context
        llm_request: The LLM request

    Returns:
        Optional[LlmResponse]: None to allow normal processing
    """
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id
    print(f"[Image Callback] Processing for agent: {agent_name} (Inv: {invocation_id})")

    # Try to get user_id from context
    user_id = None
    if hasattr(callback_context, 'state') and callback_context.state:
        user_id = callback_context.state.get('user_id')
    
    print(f"[Image Callback] User ID: {user_id}")

    # Get the last user message parts
    last_user_message_parts = []
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts:
            last_user_message_parts = llm_request.contents[-1].parts

    print(f"[Image Callback] User message parts count: {len(last_user_message_parts)}")

    # Process any image parts we found
    image_count = 0
    uploaded_urls = []

    for part in last_user_message_parts:
        # Debug info
        print(f"[Image Callback] Examining part type: {type(part)}")

        # Make sure it's an image with mime type and data
        if not hasattr(part, "inline_data") or not part.inline_data:
            continue

        mime_type = getattr(part.inline_data, "mime_type", None)
        if not mime_type or not mime_type.startswith("image/"):
            continue

        image_data = getattr(part.inline_data, "data", None)
        if not image_data:
            continue

        # We have an image to upload
        image_count += 1
        print(f"[Image Callback] Found image #{image_count}")

        # Upload to GCS
        try:
            public_url = upload_user_image_to_gcs(
                image_data=image_data,
                mime_type=mime_type,
                user_id=user_id,
                image_count=image_count
            )
            
            if public_url:
                uploaded_urls.append(public_url)
                print(f"[Image Callback] Successfully uploaded image #{image_count}")
            else:
                print(f"[Image Callback] Failed to upload image #{image_count}")
                
        except Exception as e:
            print(f"[Image Callback] Error processing image #{image_count}: {str(e)}")

    # Log the total number of images processed
    if image_count > 0:
        print(f"[Image Callback] Processed {image_count} images")
        print(f"[Image Callback] Successfully uploaded {len(uploaded_urls)} images to GCS")
        
        # Optionally: Store URLs in context for later use
        if hasattr(callback_context, 'state') and callback_context.state:
            if 'uploaded_images' not in callback_context.state:
                callback_context.state['uploaded_images'] = []
            callback_context.state['uploaded_images'].extend(uploaded_urls)

    # Continue with normal execution
    return None
