from .prompt import WRITTER_AGENT_INSTRUCTION2
from ...tools.callback import before_model_callback
from ...tools.gemini_tool import generate_social_media_post_image
 
from ...tools.firestore_service import save_post_days,get_publication_plan
from google.adk.agents import Agent
from google.adk.tools import agent_tool
from ..writter_only.agent import create_image_agent
from ...tools.utils import  get_todays_date
writer_agent= Agent(
    name="FacebookContentWriterAgent",
    model="gemini-2.5-pro-preview-05-06",
    before_model_callback=before_model_callback,
    description="Tu es l'agent charge de Rédacteur de Contenu optimise pour Facebook",
    instruction=WRITTER_AGENT_INSTRUCTION2,
    tools=[get_publication_plan,agent_tool.AgentTool(create_image_agent),save_post_days,get_todays_date]
)