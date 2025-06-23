from google.adk.agents import Agent
from ...tools.setter_tools import get_page_posts, get_post_comments,filter_negative_comments, delete_post, delete_comment
from .prompt import SETTER_INSTRUCTIONS


setter_agent=Agent(
    name="CommunityModeratorAssistant",
    model="gemini-2.0-flash",
    description="Tu es l'agent charge de la gestion des commentaires et des post sur les publications Facebook.",
    instruction=SETTER_INSTRUCTIONS,
    tools=[get_page_posts, get_post_comments,filter_negative_comments, delete_post, delete_comment]
)