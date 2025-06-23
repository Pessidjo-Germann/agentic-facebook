# Dans tools/analyst_tools.py

import os
import requests
import json
from datetime import datetime, timedelta
from google.adk.tools.tool_context import ToolContext  
import traceback  
from typing import Dict, Any  

 
GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
 
def _get_fb_credentials(tool_context: ToolContext) -> tuple[str | None, str | None]:
    """Internal helper to retrieve and verify FB credentials from context."""
    page_id = tool_context.state.get("user:fb_page_id")
    access_token = tool_context.state.get("user:fb_access_token")
    if not page_id or not access_token:
        print(f"  (Analyst Tool Helper) Erreur: Credentials FB manquants pour user {tool_context.user_id}")
        return None, None
    return page_id, access_token

def _handle_api_error(func_name: str, e: requests.exceptions.RequestException) -> Dict[str, Any]:
    """Internal helper to format API/Network errors as JSON."""
    error_code = "NETWORK_ERROR"
    error_msg = f"Network error during '{func_name}': {str(e)}"
    status_code = None

    if isinstance(e, requests.exceptions.HTTPError):
        error_code = "FB_API_ERROR"
        status_code = e.response.status_code
        error_msg = f"Facebook API error ({status_code}) during '{func_name}'"
        try:
            fb_error = e.response.json().get("error", {})
            error_msg += f": {fb_error.get('message', e.response.text)}"
        except json.JSONDecodeError:
            error_msg += f". Raw response: {e.response.text}"

    print(f"  (Analyst Tool Error) {error_msg}")
    traceback.print_exc()
    return {"status": "error", "code": error_code, "message": error_msg, "http_status": status_code}

def _handle_internal_error(func_name: str, e: Exception) -> Dict[str, Any]:
     """Internal helper to format unexpected errors as JSON."""
     error_msg = f"Unexpected error in '{func_name}': {str(e)}"
     print(f"  (Analyst Tool Error) {error_msg}")
     traceback.print_exc()
     return {"status": "error", "code": "INTERNAL_TOOL_ERROR", "message": error_msg}

 
def analyze_weekly_performance(tool_context: ToolContext) -> str:
    """
    Analyse les performances de la semaine écoulée pour la page Facebook de l'utilisateur.
    Lit PAGE_ID et ACCESS_TOKEN depuis la session et sauvegarde le rapport.
    """
    func_name = "analyze_weekly_performance"
    print(f"--- Tool: {func_name} appelé (Session-aware) ---")
    user_id = tool_context.user_id

    # --- 1. Récupérer et Vérifier les Identifiants ---
    page_id, access_token = _get_fb_credentials(tool_context)
    if not page_id:
        return json.dumps({"status": "error", "code": "FB_CREDENTIALS_MISSING", "message": "Identifiants FB manquants dans la session."})

    # --- 2. Logique d'Analyse ---
    try:
        # Définir la période d'analyse (semaine précédente complète)
        today = datetime.today()
        # Dimanche dernier (fin de la semaine précédente)
        last_sunday_dt = today - timedelta(days=today.weekday() + 1)
        # Samedi précédent le dimanche dernier (début de la semaine précédente)
        prev_saturday_dt = last_sunday_dt - timedelta(days=1)
        # Lundi précédent ce samedi (encore une semaine en arrière pour le 'since')
        # Ou simplement prendre le Dimanche à 00:00 comme début ? Clarifions la période exacte.
        # Option 1: Semaine de Lundi à Dimanche précédent
        start_of_last_week = last_sunday_dt - timedelta(days=6) # Lundi dernier
        end_of_last_week = last_sunday_dt - timedelta(seconds=1) # Dimanche dernier 23:59:59

        # Option 2: 7 derniers jours glissants ? Le prompt FB 'week' est peut-être plus simple.        # Let's stick with API's 'week' logic for now.

        # Using Insights API with 'period=week'
        print(f"  Retrieving page metrics for the week...")
        page_metrics = [
            "page_impressions_unique", # Use unique to better reflect reach
            "page_post_engagements", # Total engagement on posts
            "page_fans", # Total number of fans at end of period
            # "page_views_total", # Less relevant for engagement
            "page_fan_adds_unique", # New fans
            "page_actions_post_reactions_total" # Total reactions
        ]
        insights_url = f"{GRAPH_API_BASE_URL}/{page_id}/insights"
        insights_params = {
            "metric": ",".join(page_metrics),
            "period": "week", # Laisse FB déterminer la semaine
            # "since": int(start_of_last_week.timestamp()), # Alternative si 'period=week' n'est pas précis
            # "until": int(end_of_last_week.timestamp()),   # Alternative
            "access_token": access_token
        }
        insights_resp = requests.get(insights_url, params=insights_params)
        insights_resp.raise_for_status()
        page_data = insights_resp.json()

        page_summary: Dict[str, Any] = {}
        # L'API Insights avec period=week retourne souvent 3 valeurs (semaine passée, 2 semaines avant, etc.)
        # On prend généralement la première valeur pour la semaine la plus récente.
        for item in page_data.get("data", []):
            if item.get("values"):
                page_summary[item["name"]] = item["values"][0].get("value") # Prendre la valeur la plus récente
            else:
                 page_summary[item["name"]] = None # ou 0

        print(f"  Métriques de page récupérées: {page_summary}")

        # --- Récupération des posts de la semaine (Optionnel mais utile) ---
        # L'API Insights ne donne pas le détail par post. Il faut fetch les posts séparément.
        # Définir la période pour récupérer les posts publiés *pendant* la semaine analysée
        # Utilisons les dates calculées start_of_last_week et end_of_last_week
        print(f"  Récupération des posts publiés entre {start_of_last_week.date()} et {end_of_last_week.date()}...")
        posts_url = f"{GRAPH_API_BASE_URL}/{page_id}/published_posts" # Utiliser published_posts
        posts_params = {
            "since": int(start_of_last_week.timestamp()),
            "until": int(end_of_last_week.timestamp()),
            "fields": "id,message,created_time,insights.metric(post_impressions_unique,post_engaged_users,post_reactions_by_type_total)", # Demander les insights directement
            "limit": 50, # Limit to avoid too much data
            "access_token": access_token
        }
        posts_resp = requests.get(posts_url, params=posts_params)
        posts_resp.raise_for_status()
        posts_data = posts_resp.json().get("data", [])
        print(f"  {len(posts_data)} posts retrieved for the period.")

        analyzed_posts = []
        for post in posts_data:
            post_id = post["id"]
            message = post.get("message", "")[:100] + "..." if post.get("message") else "[No Text/Media Post]"
            created_time = post.get("created_time")
            post_insights_data = post.get("insights", {}).get("data", [])

            post_summary = {
                "post_id": post_id,
                "message_snippet": message,
                "created_time": created_time,
                "metrics": {}
            }

            for metric in post_insights_data:
                metric_name = metric.get("name")
                # La valeur est souvent dans une liste, prendre la première
                metric_value = metric.get("values", [{}])[0].get("value", 0)
                post_summary["metrics"][metric_name] = metric_value

            analyzed_posts.append(post_summary)        # Sort posts by engagement if possible
        if analyzed_posts:
            try:
                 analyzed_posts.sort(key=lambda p: p["metrics"].get("post_engaged_users", 0), reverse=True)
            except Exception as e_sort:
                 print(f"  Warning: Unable to sort posts by engagement: {e_sort}")


        # --- 3. Assemblage du Rapport Final ---
        # Utiliser les dates de début/fin calculées pour la période
        report = {
            "analysis_date": datetime.now().isoformat(),
            "summary_period": f"{start_of_last_week.date()} to {end_of_last_week.date()}",
            "page_summary_metrics": page_summary,
            "posts_analyzed": analyzed_posts # Inclure les données détaillées des posts
        }        # --- 4. Report Saving ---
        # Using a subfolder per user would be better in multi-tenant
        user_analytics_dir = os.path.join("analytics", user_id)
        os.makedirs(user_analytics_dir, exist_ok=True)
        # Name the file with the end-of-week date for uniqueness
        report_filename = f"report_{end_of_last_week.date()}.json"
        file_path = os.path.join(user_analytics_dir, report_filename)

        print(f"  Saving report to: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        success_msg = f"Weekly analysis report generated and saved in {file_path}."
        print(f"  (Tool {func_name}) Success.")
        # Returning the complete report in addition to the message can be useful to the agent
        return json.dumps({
            "status": "success",
            "message": success_msg,
            "report_file": file_path,
            "report_data": report # Also return the data
            })

    # --- Gestion des Erreurs API/Réseau/Internes ---
    except requests.exceptions.RequestException as e:
        return json.dumps(_handle_api_error(func_name, e))
    except Exception as e:
         return json.dumps(_handle_internal_error(func_name, e))