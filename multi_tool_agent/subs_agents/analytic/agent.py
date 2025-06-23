from google.adk.agents import Agent,LlmAgent
from ...tools.analyst_tools import analyze_weekly_performance
from .prompt import ANALYTIC_PROMPTS
from google.adk.tools import agent_tool
from google.adk.code_executors import BuiltInCodeExecutor
from ...tools.report_tools import get_demographics, get_posts_performance, get_page_insights
from ...tools.firestore_service import get_page_info

code_agent = Agent(
    name='CodeAgent',
    model='gemini-2.0-flash',
    instruction="""Tu es un expert python, quand on t'envoie un rapport sous forme de text,
     ton role est d'ecrire et executer du code python pour transformer ce text en pdf.
    Return only the final numerical result.
    """,
    code_executor=BuiltInCodeExecutor(),
   
)

analyst_agent=Agent(
    name="FacebookReportAgent",
    model="gemini-2.0-flash",
    description="Tu es l'agent en charge d'ecrire des rapport pour l'utilisateur.",
    tools=[agent_tool.AgentTool(code_agent), get_demographics, get_posts_performance, get_page_insights, get_page_info],
    instruction=ANALYTIC_PROMPTS,
)