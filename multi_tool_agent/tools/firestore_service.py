# # services/firestore_service.py
# import json
# import requests
# import os

# from google.cloud import firestore
# from google.cloud.firestore_v1 import SERVER_TIMESTAMP
# from google.adk.tools.tool_context import ToolContext
# from google.cloud import storage 
 
# # Initialise Firestore
# db = firestore.Client()

GCS_BUCKET_NAME="facebook-agent"
BUCKET_NAME = "gs://"+GCS_BUCKET_NAME


import json
import requests
from datetime import datetime
from typing import Dict, Any, List

from google.cloud import firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from google.adk.tools.tool_context import ToolContext

# === FIRESTORE CLIENT ===
db = firestore.Client(project="facebook-agent-461716")
 
def remove_sentinels(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    This function recursively traverses the dictionary or list to remove
    all values of type `SERVER_TIMESTAMP` (sentinels) before sending them to Firestore.
    """
    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                cleaned_data[key] = remove_sentinels(value)
            elif isinstance(value, list):
                cleaned_data[key] = [remove_sentinels(item) if isinstance(item, dict) else item for item in value]
            elif value == SERVER_TIMESTAMP:
                cleaned_data[key] = None  # Remplacer par `None` ou une autre valeur par défaut
            else:
                cleaned_data[key] = value
        return cleaned_data
    elif isinstance(data, list):
        return [remove_sentinels(item) if isinstance(item, dict) else item for item in data]
    else:
        return data
    


# === CONTEXT ===
def get_user_id(tool_context: ToolContext) -> str:
    user_id = tool_context.state.get("user_id")
    if not user_id:
        raise ValueError("user_id missing in context.")
    return user_id

# === FACEBOOK ===
def get_page_info(tool_context: ToolContext) -> Dict[str, Any]:
    try:
        page_id = tool_context.state["page_id"]
        access_token = tool_context.state["access_token"]
        url = f"https://graph.facebook.com/v22.0/{page_id}"
        params = {
            "fields": "name,about,description,category",
            "access_token": access_token
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        page_info = {
            "name_page": data.get("name"),
            "about": data.get("about"),
            "description": data.get("description"),
            "category": data.get("category")
        }
        save_page_info(tool_context, page_info)
        return {"status": "success", "page_info": page_info}
    except Exception as e:
        return {"status": "error", "message": f"Error retrieving page info: {str(e)}"}

def get_facebook_credentials(user_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    try:
        doc_ref = db.collection("users").document(user_id)\
                    .collection("facebook_credentials")\
                    .document("current_credentials")
        doc = doc_ref.get()
        if not doc.exists:
            return {"status": "error", "message": "No credentials available for this user."}
        
        credentials = doc.to_dict()
        tool_context.state['page_id'] = credentials.get("page_id")
        tool_context.state['access_token'] = credentials.get("access_token")
        return {"status": "success", "credentials": credentials}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_page_info(tool_context: ToolContext, page_info: Dict[str, Any]) -> None:
    user_id = get_user_id(tool_context)
    db.collection("users").document(user_id)\
      .collection("page_info")\
      .document("current_page")\
      .set(page_info)

# === MARKETING PLAN ===
def save_marketing_plan(plan_data: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    try:
        user_id = get_user_id(tool_context)
        
        # Clean sentinels in `plan_data` before sending
        plan_data = remove_sentinels(plan_data)
        
        plan_data["timestamp"] = SERVER_TIMESTAMP
        doc_ref = db.collection("users").document(user_id) \
                        .collection("marketing_plans") \
                        .document()
        doc_ref.set(plan_data)
        return {"status": "success", "message": "Plan saved.", "plan_id": doc_ref.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_publication_plan(post_data: Dict[str, Any], tool_context: ToolContext) -> Dict[str, str]:
    try:
        user_id = get_user_id(tool_context)
        
        # Clean sentinels in `post_data` before sending
        post_data = remove_sentinels(post_data)
        
        post_data["createdAt"] = SERVER_TIMESTAMP
        db.collection("users").document(user_id).collection("publication_plans").document().set(post_data)
        return {"status": "success", "message": "Publication plan saved."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_latest_marketing_plan(user_id: str) -> Dict[str, Any]:
    try:
        docs = db.collection("users").document(user_id)\
                  .collection("marketing_plans")\
                  .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                  .limit(1).get()
        if not docs:
            return {"status": "error", "message": "No plan found."}
        return {"status": "success", "data": docs[0].to_dict()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_publication_plan(tool_context: ToolContext) -> Dict[str, Any]:
    try:
        user_id = get_user_id(tool_context)
        docs = db.collection("users").document(user_id)\
                  .collection("publication_plans").stream()
        plans = [doc.to_dict() for doc in docs]
        return {"status": "success", "publication_plans": plans}
    except Exception as e:
        return {"status": "error", "message": str(e)}
# === POST DAYS ===
def save_post_days(post_days: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    try:
        user_id = get_user_id(tool_context)
        days_to_save = post_days.get("days", post_days)
        db.collection("users").document(user_id)\
            .collection("post_days")\
            .document("current_days")\
            .set({"days": days_to_save})
        return {"status": "success", "message": "Days saved."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_post_days(tool_context: ToolContext) -> Dict[str, Any]:
    try:
        user_id = get_user_id(tool_context)
        doc = db.collection("users").document(user_id)\
                  .collection("post_days")\
                  .document("current_days").get()
        if not doc.exists:
            return {"status": "error", "message": "No days defined."}
        return {"status": "success", "days": doc.to_dict().get("days", [])}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === FORMATTING ===
def format_post_days_by_date(post_days_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    days = post_days_response.get("days", [])
    if isinstance(days, dict) and 'days' in days:
        days = days['days']

    formatted = []
    for item in days:
        if isinstance(item, dict):
            time_str = item.get("publish_time", "")
            try:
                date_only = datetime.strptime(time_str, "%Y-%m-%d %H:%M").date().isoformat()
            except:
                date_only = "unknown"
            formatted.append({
                "date": date_only,
                "text": item.get("post_text", ""),
                "image_path": item.get("image_path", ""),
                "publish_time": time_str
            })
        elif isinstance(item, str):
            try:
                if len(item) == 10:
                    date_only = item
                else:
                    date_only = datetime.strptime(item, "%Y-%m-%d %H:%M").date().isoformat()
            except:
                date_only = "unknown"
            formatted.append({
                "date": date_only,
                "text": "",
                "image_path": "",
                "publish_time": item
            })
    return formatted

def filter_posts_by_date(posts: List[Dict[str, Any]], target_date: str) -> List[Dict[str, Any]]:
    return [post for post in posts if post["date"] == target_date]

def get_posts_for_date(tool_context: ToolContext, target_date: str) -> Dict[str, Any]:
    raw = get_post_days(tool_context)
    if raw.get("status") != "success":
        return raw
    formatted = format_post_days_by_date(raw)
    filtered = filter_posts_by_date(formatted, target_date)
    return {
        "status": "success",
        "message": f"{len(filtered)} post(s) for {target_date}.",
        "posts": filtered
    }
