from .prompt import MARKETINGS_PROMPTS
import os
import sys

from google.adk.agents import Agent
from ...tools.firestore_service import get_page_info,get_latest_marketing_plan,save_marketing_plan
import json
import os
from google.adk.sessions import Session
from google.adk.sessions import VertexAiSessionService




marketing_agent = Agent(
    name="MarketingAgent",
    model="gemini-2.0-flash",
    description="Creates a detailed persona for a Facebook page based on its title and main objective.",
    instruction=MARKETINGS_PROMPTS,
    tools=[get_latest_marketing_plan,get_page_info,save_marketing_plan],
)
