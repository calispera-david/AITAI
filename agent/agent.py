from google.adk.agents.llm_agent import Agent
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")


with open(KEY_FILE, "r") as f: 
    api_key =  f.read().strip()
os.environ["GOOGLE_API_KEY"] = api_key

agent = Agent(
    model='gemini-2.5-flash',
    name='agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
