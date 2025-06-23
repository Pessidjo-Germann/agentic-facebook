from google.adk.agents import Agent
from ...tools.publisher_tool import publish_facebook_post,load_post_day,save_posts_id
from ...tools.firestore_service import get_posts_for_date
from .prompt import PUBLISHER_INSTRUCTIONS
from ...tools.utils import  get_todays_date
publisher_agent=Agent(
    name="FacebookPublisherAgent",
    model="gemini-2.0-flash",
    description="Tu es l'agent charge de la publication des post sur les plateformes",
    instruction=PUBLISHER_INSTRUCTIONS,
    tools=[get_posts_for_date,publish_facebook_post,get_todays_date]
)