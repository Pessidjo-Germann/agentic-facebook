import os
import json
from google.cloud import storage
import requests
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from datetime import date
from google.adk.tools.tool_context import ToolContext
current_dir = os.path.dirname(os.path.abspath(__file__))
POST_DAY_FILE= os.path.join(current_dir, "../../data/post_day.json")
GRAPH_API_VERSION = "v22.0"

BUCKET_NAME="facebook_agent"
# load_dotenv()

# PAGE_ID = os.getenv("FB_PAGE_ID")
# ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
def load_facebook_credentials(user_id: str) -> dict:
    """Charge les credentials Facebook d'un user depuis GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"facebook_credentials/{user_id}.json")

    if not blob.exists():
        raise FileNotFoundError(f"Aucun credentials trouvé pour l'utilisateur {user_id}.")

    data = json.loads(blob.download_as_text())
    return data
def publish_facebook_post(
    user_id: str,
    message: str,
    image_path: str,
    publish_time: str,
    tool_context: ToolContext,
) -> str:
    """
    Publie ou programme un message sur une page Facebook.
    Accepte les images locales OU distantes (URL).

    Args:
        user_id: ID de l'utilisateur (non utilisé ici mais requis pour cohérence).
        message: Texte à publier.
        image_path: Chemin vers une image locale ou URL vers une image distante.
        publish_time: Date/heure planifiée ("YYYY-MM-DD HH:MM").
        tool_context: Contexte ADK avec page_id et access_token.

    Returns:
        Résultat JSON avec le statut de publication.
    """
    try:
        publish_options = {}
        PAGE_ID = tool_context.state["page_id"]
        ACCESS_TOKEN = tool_context.state["access_token"]

        if publish_time:
            dt = datetime.strptime(publish_time, "%Y-%m-%d %H:%M")
            timestamp = int(dt.timestamp())
            publish_options["published"] = False
            publish_options["scheduled_publish_time"] = timestamp

        post_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}/feed"

        if image_path:
            upload_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PAGE_ID}/photos"

            # Cas 1 : Lien URL distant
            if image_path.startswith("http://") or image_path.startswith("https://"):
                upload_payload = {
                    'url': image_path,
                    'published': 'false',
                    'access_token': ACCESS_TOKEN
                }
                upload_resp = requests.post(upload_url, data=upload_payload)

            # Cas 2 : Fichier local
            elif os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    files = {'source': image_file}
                    upload_payload = {
                        'published': 'false',
                        'access_token': ACCESS_TOKEN
                    }
                    upload_resp = requests.post(upload_url, files=files, data=upload_payload)
            else:
                raise Exception("Image introuvable (ni URL valide ni fichier local existant)")

            if upload_resp.status_code != 200:
                raise Exception(f"Échec upload image : {upload_resp.text}")

            photo_id = upload_resp.json().get("id")
            post_payload = {
                "message": message,
                "attached_media": [{"media_fbid": photo_id}],
                "access_token": ACCESS_TOKEN,
                **publish_options
            }
        else:
            # Pas d’image
            post_payload = {
                "message": message,
                "access_token": ACCESS_TOKEN,
                **publish_options
            }

        post_resp = requests.post(post_url, json=post_payload)
        if post_resp.status_code == 200:
            post_id = post_resp.json().get("id")
            status_msg = "scheduled" if publish_time else "published"
            return json.dumps({
                "status": "success",
                "message": f"Post {status_msg} successfully! ID: {post_id}",
                "post_id": post_id
            })
        else:
            raise Exception(post_resp.text)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during Facebook publication: {str(e)}"
        })

def load_post_day() -> dict:
    """
    Load the daily posts data from the JSON file.
    
    Returns:
        Dictionary containing the daily posts data.
    """
    try:
        if os.path.exists(POST_DAY_FILE):
            with open(POST_DAY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"Error loading post day data: {str(e)}")
        return {}

def save_posts_id(posts_data: dict) -> str:
    """
    Save post IDs and related data to the JSON file.
    
    Args:
        posts_data: Dictionary containing post data to save.
        
    Returns:
        JSON string with status message.
    """
    try:
        # Load existing data
        existing_data = load_post_day()
        
        # Update with new data
        existing_data.update(posts_data)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(POST_DAY_FILE), exist_ok=True)
        
        # Save updated data
        with open(POST_DAY_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
        return json.dumps({
            "status": "success",
            "message": "Post IDs saved successfully"
        })
    except Exception as e:
        return json.dumps({
            "status": "error", 
            "message": f"Error saving post IDs: {str(e)}"
        })