# Dans tools/setter_tools.py

import os
import json
import requests
# Supprimer load_dotenv si plus utilisé
# from dotenv import load_dotenv
from typing import List, Dict, Any, Union, Optional  
from google.adk.tools.tool_context import ToolContext # <-- IMPORT ESSENTIEL
import traceback # Pour logging d'erreur

# --- Configuration API (Optionnel) ---
GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
 

def _handle_api_error(func_name: str, e: requests.exceptions.RequestException) -> Dict[str, Any]:
    """Helper interne pour formater les erreurs API/Réseau en JSON."""
    error_code = "NETWORK_ERROR"
    error_msg = f"Erreur réseau lors de '{func_name}': {str(e)}"
    status_code = None

    if isinstance(e, requests.exceptions.HTTPError):
        error_code = "FB_API_ERROR"
        status_code = e.response.status_code
        error_msg = f"Erreur API Facebook ({status_code}) lors de '{func_name}'"
        try:
            fb_error = e.response.json().get("error", {})
            error_msg += f": {fb_error.get('message', e.response.text)}"
        except json.JSONDecodeError:
            error_msg += f". Réponse brute: {e.response.text}"

    print(f"  (Setter Tool Error) {error_msg}")
    traceback.print_exc()
    return {"status": "error", "code": error_code, "message": error_msg, "http_status": status_code}

def _handle_internal_error(func_name: str, e: Exception) -> Dict[str, Any]:
     """Helper interne pour formater les erreurs inattendues en JSON."""
     error_msg = f"Erreur inattendue dans '{func_name}': {str(e)}"
     print(f"  (Setter Tool Error) {error_msg}")
     traceback.print_exc()
     return {"status": "error", "code": "INTERNAL_TOOL_ERROR", "message": error_msg}


# --- Fonctions Outils Exposées ---

def get_page_posts(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Récupère les posts publiés sur la page Facebook de l'utilisateur.
    Lit PAGE_ID et ACCESS_TOKEN depuis la session.
    """
    func_name = "get_page_posts"
    print(f"--- Tool: {func_name} appelé (Session-aware) ---")
    page_id, access_token = tool_context.state.get('user:fb_page_id'), tool_context.state.get('user:fb_access_token')
    if not page_id:
        return {"status": "error", "code": "FB_CREDENTIALS_MISSING", "message": "Identifiants FB manquants dans la session."}

    url = f"{GRAPH_API_BASE_URL}/{page_id}/posts"
    params = {
        "access_token": access_token,
        "fields": "id,message,created_time", # Ajouter d'autres champs si nécessaire
        "limit": 25 # Limiter le nombre de posts retournés par défaut
    }
    print(f"  (Tool {func_name}) Appel GET vers {url}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Vérifie les erreurs HTTP
        print(f"  (Tool {func_name}) Succès.")
        
        return response.json()
    except requests.exceptions.RequestException as e:
        return _handle_api_error(func_name, e)
    except Exception as e:
         return _handle_internal_error(func_name, e)


def get_post_comments(post_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Récupère les commentaires pour un post spécifique.
    Lit ACCESS_TOKEN depuis la session.
    """
    func_name = "get_post_comments"
    print(f"--- Tool: {func_name} appelé pour post_id={post_id} (Session-aware) ---")
    # On n'a besoin que du token ici, mais on le récupère via le helper
    _, access_token = tool_context.state.get('user:fb_page_id'), tool_context.state.get('user:fb_access_token')
    if not access_token:
        return {"status": "error", "code": "FB_CREDENTIALS_MISSING", "message": "Access Token FB manquant dans la session."}

    # Validation simple de post_id (peut contenir '_')
    if not post_id or not isinstance(post_id, str) or len(post_id.split('_')) < 2 :
         print(f"  (Tool {func_name}) Erreur: post_id invalide '{post_id}'")
         return {"status": "error", "code": "INVALID_INPUT", "message": f"L'argument post_id '{post_id}' semble invalide."}

    url = f"{GRAPH_API_BASE_URL}/{post_id}/comments"
    params = {
        "access_token": access_token,
        "fields": "id,message,from{id,name},created_time", 
        "limit": 50 
    }
    print(f"  (Tool {func_name}) Appel GET vers {url}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print(f"  (Tool {func_name}) Succès.")
        return response.json()
    except requests.exceptions.RequestException as e:
        return _handle_api_error(func_name, e)
    except Exception as e:
         return _handle_internal_error(func_name, e)


def filter_negative_comments(comments_data: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Filtre les commentaires négatifs à partir des données JSON brutes de l'API FB.
    Ne nécessite pas d'identifiants FB, mais on garde tool_context pour la cohérence.
    Retourne un dictionnaire avec statut et la liste des commentaires négatifs.
    """
    func_name = "filter_negative_comments"
    print(f"--- Tool: {func_name} appelé ---")
    # Liste de mots-clés simple (peut être améliorée avec une analyse de sentiment IA plus tard)
    negative_keywords = ["bad", "terrible", "awful", "hate", "dislike", "problem", "issue", "arnaque", "nul", "déçu", "mauvais"] # Ajout de mots français
    negative_comments_found = []

    if not isinstance(comments_data, dict) or 'data' not in comments_data:
         msg = "Les données d'entrée ('comments_data') doivent être un dictionnaire JSON provenant de l'API get_post_comments (avec une clé 'data')."
         print(f"  (Tool {func_name}) Erreur: {msg}")
         return {"status": "error", "code": "INVALID_INPUT", "message": msg}

    comments_list = comments_data['data']
    if not isinstance(comments_list, list):
        msg = "La clé 'data' dans les données d'entrée n'est pas une liste."
        print(f"  (Tool {func_name}) Erreur: {msg}")
        return {"status": "error", "code": "INVALID_INPUT", "message": msg}

    print(f"  Filtrage de {len(comments_list)} commentaires...")
    for comment in comments_list:
        if isinstance(comment, dict) and 'message' in comment and isinstance(comment['message'], str):
            message_lower = comment['message'].lower()
            for keyword in negative_keywords:
                if keyword in message_lower:
                    negative_comments_found.append(comment)
                    break # Passer au commentaire suivant dès qu'un mot-clé est trouvé

    print(f"  {len(negative_comments_found)} commentaires négatifs potentiels trouvés.")
    return {
        "status": "success",
        "negative_comments": negative_comments_found,
        "message": f"{len(negative_comments_found)} commentaires négatifs potentiels identifiés."
        }


def delete_post(post_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Supprime un post de la page Facebook de l'utilisateur.
    Lit ACCESS_TOKEN depuis la session.
    """
    func_name = "delete_post"
    print(f"--- Tool: {func_name} appelé pour post_id={post_id} (Session-aware) ---")
    _, access_token = tool_context.state.get('user:fb_page_id'), tool_context.state.get('user:fb_access_token')
    if not access_token:
        return {"status": "error", "code": "FB_CREDENTIALS_MISSING", "message": "Access Token FB manquant dans la session."}

    if not post_id or not isinstance(post_id, str) or len(post_id.split('_')) < 2 :
         print(f"  (Tool {func_name}) Erreur: post_id invalide '{post_id}'")
         return {"status": "error", "code": "INVALID_INPUT", "message": f"L'argument post_id '{post_id}' semble invalide."}

    url = f"{GRAPH_API_BASE_URL}/{post_id}"
    params = {
        "access_token": access_token,
    }
    print(f"  (Tool {func_name}) Appel DELETE vers {url}")
    try:
        response = requests.delete(url, params=params)
        response.raise_for_status()
        result = response.json() # La réponse de FB pour un DELETE réussi est souvent {"success": true}
        print(f"  (Tool {func_name}) Succès: {result}")
        # Renvoyer un message de succès clair en plus de la réponse FB
        return {"status": "success", "message": f"Post {post_id} supprimé avec succès.", "api_response": result}
    except requests.exceptions.RequestException as e:
        return _handle_api_error(func_name, e)
    except Exception as e:
         return _handle_internal_error(func_name, e)


def delete_comment(comment_id: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Supprime un commentaire d'un post.
    Lit ACCESS_TOKEN depuis la session.
    """
    func_name = "delete_comment"
    print(f"--- Tool: {func_name} appelé pour comment_id={comment_id} (Session-aware) ---")
    _, access_token = tool_context.state.get('user:fb_page_id'), tool_context.state.get('user:fb_access_token')
    if not access_token:
        return {"status": "error", "code": "FB_CREDENTIALS_MISSING", "message": "Access Token FB manquant dans la session."}

    # Validation simple de comment_id (peut contenir '_')
    if not comment_id or not isinstance(comment_id, str) or len(comment_id.split('_')) < 2 :
         print(f"  (Tool {func_name}) Erreur: comment_id invalide '{comment_id}'")
         return {"status": "error", "code": "INVALID_INPUT", "message": f"L'argument comment_id '{comment_id}' semble invalide."}

    url = f"{GRAPH_API_BASE_URL}/{comment_id}"
    params = {
        "access_token": access_token,
    }
    print(f"  (Tool {func_name}) Appel DELETE vers {url}")
    try:
        response = requests.delete(url, params=params)
        response.raise_for_status()
        result = response.json() # Souvent {"success": true}
        print(f"  (Tool {func_name}) Succès: {result}")
        return {"status": "success", "message": f"Commentaire {comment_id} supprimé avec succès.", "api_response": result}
    except requests.exceptions.RequestException as e:
        return _handle_api_error(func_name, e)
    except Exception as e:
         return _handle_internal_error(func_name, e)