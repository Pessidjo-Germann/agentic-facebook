import vertexai
from multi_tool_agent.agent import root_agent
from vertexai import agent_engines
from multi_tool_agent.tools.gs_builder import gcs_artifact_service_builder
from vertexai.preview import reasoning_engines
from multi_tool_agent.tools.firestore_service import BUCKET_NAME
from dotenv import load_dotenv
PROJECT_ID = "facebook-agent-461716"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://run-sources-facebook-agent-461716-us-central1"
load_dotenv()
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
   staging_bucket=STAGING_BUCKET,
)

requirements = [
    "google-cloud-aiplatform[agent_engines,adk]",
    "openai",
    "Pillow",
    "google-adk",
    "uvicorn[standard]",
    "fastapi",
    "pydantic",
    "requests",
    "psycopg2-binary",
    "python-dateutil",
    "google-cloud-storage",
    "google-cloud-firestore",
    "cloudpickle>=2.0.0"
    # any other dependencies
]
app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,  
  
)
 
extra_packages = ["./multi_tool_agent"]

remote_agent = agent_engines.create(
    app,                    
    requirements=requirements,      
    extra_packages=extra_packages, 
 
)

# # agent_engines.list()

# agent_engines.update(resource_name='', agent_engine=root_agent, requirements=requirements)

