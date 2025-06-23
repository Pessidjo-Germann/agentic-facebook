from google.adk.agents import Agent
from ...tools.firestore_service import get_page_info,get_latest_marketing_plan,save_publication_plan
from .prompt import SYSTEM_INSTRUCTION
from ...tools.utils import  get_todays_date
strategy_agent = Agent(
    name="EditorialPlannerAgent",
    model="gemini-2.0-flash",
    description=" Votre mission est de concevoir chaque semaine un plan de contenu éditorial cohérent, varié, engageant et parfaitement aligné avec le plan marketing global",
    instruction=SYSTEM_INSTRUCTION,
    tools=[get_page_info,get_latest_marketing_plan,save_publication_plan,get_todays_date]
)