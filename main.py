from agent.agent import agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google import genai
import os
from pathlib import Path
import asyncio

PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")


def verify_api_key_simple():
    try:
        client = genai.Client()

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Respond ONLY with 'API key is valid'"
        )
        
        if response.text.strip() == "API key is valid":
            print("API key successfully verified!")
            return True
        else:
            print("Model responded, but with unexpected text.")
            return False
            
    except Exception as e:
        print(f"API key is invalid or connection failed: {e}")
        exit()

verify_api_key_simple()


chat_memory = InMemorySessionService()
chat_runner = Runner(agent = agent, session_service = chat_memory, app_name = "csv_analyzer")

session = asyncio.run(chat_memory.create_session(
    app_name="csv_analyzer", 
    user_id="default_user", 
    session_id="user_1"
))

msg = input("USER: ")
while msg:
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=msg)]
    )

    events = chat_runner.run(
    user_id="default_user",
    session_id="user_1", 
    new_message=user_message
    )

    for event in events:
        if event.content and event.content.parts:
            final_text = event.content.parts[0].text
            print("AI: ", final_text)
    msg = input("USER: ")
