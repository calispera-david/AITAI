from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from google.genai import types
from google import genai
from google.adk.agents.llm_agent import Agent
from pathlib import Path
import os
import asyncio


# File directories
# Note, the agent does not need the Data directories at this moment because the api key is stored in the project root, but later in the future, the api key will be stored in the data directory and it will change
PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
# this should never happen as the agent is initialized after the main.py has already created the file, but just in case if there is no key file it will crash
if not os.path.exists(KEY_FILE):
    exit()

with open(KEY_FILE, "r") as f: 
    api_key =  f.read().strip()
os.environ["GOOGLE_API_KEY"] = api_key

# the MainAgent class is responsible for initializing the agent, loading the chat history and generating responses
# it uses Google's ADK library, however I would advise against using it as the documentation is very poor at the moment of starting this project
class MainAgent:
    # init function
    def __init__(self,session_id):
        # saves the session_id
        self.session_id = session_id
        # initializes the agent with the model, name, description and instruction
        self.agent = Agent(
            model='gemini-2.5-flash',
            name='agent',
            description='A helpful assistant for user questions.',
            instruction='Answer user questions to the best of your knowledge',
        )
        # initializes the memory service and the runner with the agent and memory service
        self.chat_memory = InMemorySessionService()
        self.chat_runner = Runner(agent = self.agent, session_service = self.chat_memory, app_name = "csv_analyzer")

        # creates a new session for the agent
        self.session = asyncio.run(self.chat_memory.create_session(
            app_name="csv_analyzer", 
            user_id="default_user", 
            session_id= self.session_id
        ))

    # a function that loads the chat history
    def load_data(self,saved_data):
        for index,item in enumerate(saved_data):
            if item["role"] == "user" or item["role"] == "agent":
                if index == len(saved_data) - 1 and item["role"] == "user":
                    # skip the last user message if it was not responded to, this should be prevented while saving but just in case..
                    continue
                # rebuilds the event, which is the format in which the agent responds and receives messages
                # this is crucial as the agent can't process other formats
                # this is a big reason why I do not recommend using this library as I couldn't find any documentation on this process and had to rely on Gemini for help
                rebuilt_event = Event(
                    author="user" if item["role"] == "user" else "agent",
                    turn_complete=True,
                    content=types.Content(
                    role= "user" if item["role"] == "user" else "model",
                    parts=[types.Part(text=item["text"])]
                    ))
                # appends the event asynchroniously, I don't even know why
                asyncio.run(self.chat_memory.append_event(self.session, rebuilt_event))
    
    # a function that generates the agent's response
    def generate_content(self,user_text):
        # turns the message into a Content type, again very poorly documented
        user_msg = types.Content(role="user", parts=[types.Part(text=user_text)])

        final_text = ""
        # sends the message and gets the events
        events = self.chat_runner.run(
            user_id="default_user",
            session_id= self.session_id, 
            new_message=user_msg            
        )
        # finds the final text or the error if the agent returns one
        for event in events:
            if hasattr(event, 'content') and event.content and event.content.parts:
                final_text = event.content.parts[0].text
                    
            # if it has an error code it puts it at the start of the error message for easier reading and/or debugging
            elif hasattr(event, 'error_code') and event.error_code:
                error_details = getattr(event, 'error_message')
                raise RuntimeError(f"{event.error_code} - {error_details}")
        # returns either the final text or an error if the text is blank, never happened but you never know what to expect
        if final_text:
            ai_reply = final_text
            return ai_reply
        else:
            raise ValueError("API returned no text. You likely hit a quota limit or safety block.")

# the APIVerifier class is responsible with verifying an API key.
class APIVerifier:
    def __init__(self,api_key):
        # the api key is feeded from main.py
        self.api_key = api_key

    
    def verify_api_key(self):
        # sets the api key as an environmental variable
        os.environ["GOOGLE_API_KEY"] = self.api_key
        try:
            # uses the most lightweight model for this process to save on tokens
            client = genai.Client()

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents="Respond ONLY with 'API key is valid'"
            )
            # if the agent responds as expected it considers the key verified
            if response.text.strip() == "API key is valid":
                return True
            else:
                # returns an error which in turn prompts the user for another API key
                return Exception(f"Got unexpected response from API: {response.text.strip()}")
                
        except Exception as e:
            return e