from agent.agent import agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google import genai
import os
from pathlib import Path
import asyncio
import threading
import datetime

from scripts.interface import AIChatApp
import tkinter as tk
from tkinter import simpledialog, messagebox

PROJECT_ROOT = Path(__file__).parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")

api_key = ""
with open(KEY_FILE, "r") as f: 
    api_key =  f.read().strip()
os.environ["GOOGLE_API_KEY"] = api_key

def _error(e):
    messagebox.showerror(f"Error Code: {e.code}",e.message)

def main():
    try:
        with open(KEY_FILE, "r") as f: 
            api_key =  f.read().strip()
        os.environ["GOOGLE_API_KEY"] = api_key
        print("api_key: ", api_key)
        os.environ["GOOGLE_API_KEY"] = api_key
        chat_memory = InMemorySessionService()
        chat_runner = Runner(agent = agent, session_service = chat_memory, app_name = "csv_analyzer")
        
        session_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        session = asyncio.run(chat_memory.create_session(
            app_name="csv_analyzer", 
            user_id="default_user", 
            session_id=session_id
        ))

        # starts the UI
        root = tk.Tk()
        app = AIChatApp(root, chat_runner, session_id)
        root.mainloop()
    except Exception as e:
        print("Initialization failed")
        print(e)
        print("line 50")

def prompt_api_key():
    key = simpledialog.askstring(
            "Valid Google API Key Required",
            "Enter your Google API key \n Other LLM options not yet available"
        )
            
    if key:
        with open(KEY_FILE, "w") as f:
            f.write(key.strip())
            
    else:
        messagebox.showerror("Error", "A valid Google API key is required to use this app.")
def verify_api_key():
    try:
        client = genai.Client()

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Respond ONLY with 'API key is valid'"
        )
        
        if response.text.strip() == "API key is valid":
            print("API key successfully verified!")
        else:
            # Prompts the user for the key
            prompt_api_key()
            
    except Exception as e:
        _error(e)
        if e.code == 400:
            # Prompts the user for the key
            prompt_api_key()
        else:
            exit()

verify_api_key()

if __name__ == "__main__":
    main()


# msg = input("USER: ")
# while msg:
#     user_message = types.Content(
#         role="user",
#         parts=[types.Part(text=msg)]
#     )

#     events = chat_runner.run(
#     user_id="default_user",
#     session_id="user_1", 
#     new_message=user_message
#     )

#     for event in events:
#         if event.content and event.content.parts:
#             final_text = event.content.parts[0].text
#             print("AI: ", final_text)
#     msg = input("USER: ")
