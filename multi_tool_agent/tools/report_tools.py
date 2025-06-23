from google.adk.tools.tool_context import ToolContext
import requests
import json
import os
from datetime import datetime
from typing import List
from google.cloud import storage
import uuid
GRAPH_API_VERSION = 'v23.0'

def get_page_metadata(
    tool_context: ToolContext
) -> dict:
    """
    Retrieves the metadata of a Facebook Page.
    Returns:
      - status: 'success' or 'error'
      - data: API response in case of success
      - message: error message if failure
    """
    PAGE_ID = tool_context.state['page_id']
    ACCESS_TOKEN = tool_context.state['access_token']
    endpoint = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}"
    params = {
        'fields': ','.join([
            'id','name','username','verification_status','category',
            'about','emails','website','phone','link',
            'fan_count','followers_count','created_time'
        ]),
        'access_token': ACCESS_TOKEN
    }
    try:
        resp = requests.get(endpoint, params=params)
        resp.raise_for_status()
        return {'status': 'success', 'data': resp.json()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}



def get_page_insights(
    metrics: List[str],
    since: str,
    until: str,
    tool_context: ToolContext
) -> dict:
    """
    Retrieves the insights of a Page.
    Args:
      - metrics: list of metrics (check availability)
      - since, until: dates 'YYYY-MM-DD'
    Returns structure similar to get_page_metadata
    """
    PAGE_ID = tool_context.state['page_id']
    ACCESS_TOKEN = tool_context.state['access_token']
    endpoint = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}/insights"
    params = {
        'metric': ','.join(metrics),
        'period': 'day',
        'since': since,
        'until': until,
        'access_token': ACCESS_TOKEN
    }
    try:
        resp = requests.get(endpoint, params=params)
        resp.raise_for_status()
        return {'status': 'success', 'data': resp.json()}
    except requests.exceptions.HTTPError as e:
        # Specific handling for deprecated metrics errors
        if 'invalid metric' in str(e).lower():
            return {
                'status': 'error', 
                'message': f'One or more metrics are deprecated: {str(e)}'
            }
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}





def get_posts_performance(
    limit: int,
    tool_context: ToolContext
) -> dict:
    """
    Retrieves posts and their insights.
    Args:
      - limit: max number of posts (recommended: max 100)
    """
    PAGE_ID = tool_context.state['page_id']
    ACCESS_TOKEN = tool_context.state['access_token']
    endpoint = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}/posts"
    
    # Security limitation recommended
    if limit > 100:
        limit = 100
    
    params = {
        'limit': limit,
        'fields': (
            'id,message,created_time,permalink_url,'
            'insights.metric(post_impressions,post_engaged_users,post_reactions_like_total,'
            'post_clicks,post_video_views)'  # Additional available metrics
        ),
        'access_token': ACCESS_TOKEN
    }
    try:
        resp = requests.get(endpoint, params=params)
        resp.raise_for_status()
        return {'status': 'success', 'data': resp.json()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def get_demographics(
    tool_context: ToolContext
) -> dict:
    """
    Retrieves demographic data lifetime.
    WARNING: Some demographic metrics have been deprecated
    """
    PAGE_ID = tool_context.state['page_id']
    ACCESS_TOKEN = tool_context.state['access_token']
    endpoint = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}/insights"
    params = {
        'metric': 'page_fans_gender_age,page_fans_country',
        'period': 'lifetime',
        'access_token': ACCESS_TOKEN
    }
    try:
        resp = requests.get(endpoint, params=params)
        resp.raise_for_status()
        return {'status': 'success', 'data': resp.json()}
    except requests.exceptions.HTTPError as e:
        if 'invalid metric' in str(e).lower():
            return {
                'status': 'warning', 
                'message': 'Demographic metrics potentially deprecated',
                'data': {}
            }
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}




def upload_pdf_to_gcs(
    pdf_path: str,
    bucket_name: str,
    destination_blob_name: str = None
) -> str:
    """
    Upload a PDF file to Google Cloud Storage and return the public URL.
    Args:
        pdf_path: Local path to the PDF file.
        bucket_name: GCS bucket name.
        destination_blob_name: Blob name in GCS (optional).
    Returns:
        Public URL of the stored PDF.
    """
    if destination_blob_name is None:
        filename = os.path.basename(pdf_path)
        today = datetime.now().strftime("%Y/%m/%d")
        destination_blob_name = f"pdfs/{today}/{uuid.uuid4().hex}_{filename}"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(pdf_path, content_type='application/pdf')

    return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"


def upload_pdf_bytes_to_gcs(
    pdf_bytes: bytes,
    bucket_name: str,
    tool_context: ToolContext
) -> str:
    """
    Direct upload of a PDF (in bytes) to GCS and returns the public URL.
    Args:
        pdf_bytes: PDF content as bytes.
        bucket_name: GCS bucket name.
        tool_context: ADK context with page_id and access_token
    Returns:
        Public URL of the stored PDF.
    """
    user_id = tool_context.state.get('user_id')
    today = datetime.now().strftime("%Y/%m/%d")
    filename = f"{uuid.uuid4().hex}.pdf"
    if user_id:
        destination_blob_name = f"users/{user_id}/pdfs/{today}/{filename}"
    else:
        destination_blob_name = f"generated_pdfs/{today}/{filename}"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(pdf_bytes, content_type='application/pdf')

    return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"