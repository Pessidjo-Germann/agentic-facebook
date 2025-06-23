from google.adk.agents import Agent
from google.adk.tools import agent_tool
from ...tools.gemini_tool import generate_social_media_post_image
from ...tools.utils import  get_todays_date
from .prompt import INSTRUCTION,INSTRUCTION2

create_image_agent = Agent(
    name="CreateImageAgent",
    model="gemini-2.5-pro-preview-05-06",
    description="Generates images for social media posts based on text prompts.",
    instruction=INSTRUCTION2,
    tools=[generate_social_media_post_image]

)
interactive_post_agent = Agent(
    name="InteractivePostCreatorAgent",
    model="gemini-2.0-flash",
    description="Generates interactive posts for social media platforms.",
    instruction=INSTRUCTION,
    tools=[agent_tool.AgentTool(create_image_agent),get_todays_date]
)
