import os
from time import time
from google.adk.agents import Agent
 
from google.adk.agents import Agent
 
from sqlalchemy import engine 
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from google.genai import types
from typing import Optional
from .tools.firestore_service import get_facebook_credentials, get_page_info
# Import sub-agents
from .subs_agents.marketing.agent import marketing_agent
from .subs_agents.strategy.agent import strategy_agent
from .subs_agents.writer.agent import writer_agent
from .subs_agents.publisher.agent import publisher_agent
from .subs_agents.setter.agent import setter_agent
from .subs_agents.analytic.agent import analyst_agent
from .subs_agents.writter_only.agent import interactive_post_agent
from .prompt import ROOT_AGENT2
 
from datetime import datetime, timezone, timedelta
import requests
from google.adk.tools.tool_context import ToolContext
# Tool to get today's date
from .tools.utils import get_todays_date
usere_id = "user_id"
def save_user_id_memory(user_id: str, tool_context: ToolContext):
    """
    Save the user_id in the tool context state and fetch page info and credentials.
    """
    tool_context.state["user_id"] = user_id
    usere_id = user_id
    us = tool_context.state.get("user_id")
    get_page_info(tool_context)
    get_facebook_credentials(user_id, tool_context)
    return {
        'status': 'success',
        'message': f"User ID {us} saved in memory."
    }

def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
    """
    Example callback to read/write state before model call.
    """
    user_id = callback_context.state.get("user_id", 0)
    name = callback_context.state.get("name", "unknown")
    callback_context.state["user_id"] = user_id
    callback_context.state["name"] = name
    return None  # Allow model call to proceed


 
root_agent = Agent(
    name="coordinator_agent",
    model="gemini-2.5-pro-preview-05-06",
    
    description="Agent that coordinates the marketing, strategy, and writer agents.",
    global_instruction=f"""
    Today's date is: {get_todays_date()}.
    Each time you want to perform an action, check the current date and time using {get_todays_date()}.
    Whenever you query a document and it is empty, you must first notify the user and see what you can do next.
    Whenever you are overwhelmed or have finished your task, you must call the coordinator.
    """,
    instruction=ROOT_AGENT2,
    sub_agents=[
        marketing_agent,
        strategy_agent,
        writer_agent,
        publisher_agent,
        setter_agent,
        analyst_agent,
        interactive_post_agent
    ],
    tools=[
        save_user_id_memory,
        get_page_info,
        get_facebook_credentials,
        get_todays_date
    ]
    
)