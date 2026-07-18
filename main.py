import os
from pathlib import Path
import asyncio
import threading
from datetime import datetime
import json

# imports what is needed for the UI and the agent
from scripts.interface import AIChatApp, Picker
from agent.agent import MainAgent, APIVerifier
# imports basic tkinter to start the UI
import tkinter as tk
from tkinter import simpledialog, messagebox
# imports platform to check the OS and import the correct button class
import platform
if platform.system() == "Windows": 
    from tkinter import Button as OSButton
else:
    from tkmacosx import Button as OSButton

# Data directories
if platform.system() == "Windows":
    DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA"),"Calispera")
    os.makedirs(DATA_DIR, exist_ok=True)
    DATA_DIR_PROJECT = os.path.join(DATA_DIR,"AITAI")
else:
    DATA_DIR = os.path.join(os.path.join(Path.home(),"Documents"),"Calispera")
    os.makedirs(DATA_DIR, exist_ok=True)
    DATA_DIR_PROJECT = os.path.join(DATA_DIR,"AITAI")
    print(DATA_DIR_PROJECT)

# File directories
PROJECT_ROOT = Path(__file__).parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
# KEY_FILE = os.path.join(DATA_DIR, ".ai_api_key")
CHATS_FOLDER  = os.path.join(DATA_DIR_PROJECT, "chats")
os.makedirs(CHATS_FOLDER, exist_ok=True)


# simple function to handle errors and display them in a messagebox
def _error(e):
    # prompts an error box 
    if hasattr(e, "code"):
        messagebox.showerror(f"Error Code: {e.code}", e.message)
    else:
        messagebox.showerror("Error", e)


            


# Main function, the heart of the program, it initializes the agent and the UI
def main():
    # global variables that need to be accessed in multiple functions
    global session_id, root, app, api_key, agent_main, saved_data
    agent_main = None
    session_id = None
    try:
        # reads the api key from the file and sets it as an environment variable for ADK
        with open(KEY_FILE, "r") as f: 
            api_key =  f.read().strip()
        os.environ["GOOGLE_API_KEY"] = api_key
        print("api_key: ", api_key)


        global launcher 
        # function to load a chat from a file, it initializes the agent with the session_id and loads the saved_data into the UI and agent, gets called from the Picker class when the load button is pressed
        def load_chat(picker_session_id, filepath):
            global session_id, agent_main, saved_data
            session_id = picker_session_id
            agent_main = MainAgent(session_id)
            saved_data = []
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    saved_data = json.load(f)
                
                agent_main.load_data(saved_data)
        # function to create a new chat, it initializes the agent with the session_id and creates an empty saved_data list, gets called from the Picker class when the create button is pressed
        def create_new_chat(picker_session_id):
            global session_id, agent_main, saved_data
            session_id = picker_session_id
            agent_main = MainAgent(session_id)
            saved_data = []
        # creates the launcher window and the launcher app itself with the Picker class
        launcher = tk.Tk()
        picker = Picker(launcher, existing_files=[f for f in os.listdir(CHATS_FOLDER) if f.endswith(".json")], load_chat=load_chat, create_new_chat=create_new_chat)
        launcher.wait_window()  # Wait for the launcher to close before proceeding
        
        if not session_id:
            exit()  # Exit if no session_id was set (user closed the launcher without selecting or creating a chat)

        # function to save the chat history before exiting the app, gets called from the AIChatApp class when the exit button is pressed
        def _save_and_exit():
            history_to_save = []
            save_file_path = os.path.join(CHATS_FOLDER,f"{session_id}.json")
            try:
                # gets the history from the app and adds every entry to the history_to_save list
                history = app.ui_history
                for index,entry in enumerate(history):
                    if not (entry["role"] == "user" and index == len(history) - 1):
                        # skips the last message if there was no response (saving while thinking even though it shouldn't happen)
                        history_to_save.append({
                            "role": entry["role"],
                            "text": entry["text"]
                        })
                # dumps the history_to_save list into a json file with the session_id as the filename
                with open(save_file_path, "w") as f:
                    json.dump(history_to_save,f)         
                root.destroy()
                        
            except Exception as e:
                # in case of an error while saving, it prompts the user if they want to exit without saving
                _error(e)
                res = messagebox.askyesno("Error", "Error while saving \nDo you want to exit without saving?")
                if res:
                    root.destroy()
        # starts the UI window and the main app itself with the AIChatApp class
        root = tk.Tk()
        app = AIChatApp(root, session_id, saved_data,agent_main, _save_and_exit)
        root.mainloop()
    except Exception as e:
        # in case of an error during initialization, it prints the error and prompts the user with an error message
        # most of the time the error is after the launcher closes, but if there is an issue during the launcher the app closes itself to avoid unexpected behavior
        print("Initialization failed")
        print(e)
        _error(e)
        exit()

# Function to prompt the user for a valid API key and then recalls verify_api_key_main() to verify the key.
def prompt_api_key():
    key = simpledialog.askstring(
            "Valid Google API Key Required",
            "Enter your Google API key \n Other LLM options not yet available"
        )
            
    if key:
        with open(KEY_FILE, "w") as f:
            f.write(key.strip())

        verify_api_key_main()
    else:
        messagebox.showerror("Error", "A valid Google API key is required to use this app.")
        exit()

# Function to get the API key from the file or prompt the user for it if the file is not found   
def get_or_request_api():
        # Checks for the file in the chosen path
        if (os.path.exists(KEY_FILE)):
            with open(KEY_FILE, "r") as f:
                key_text = f.read().strip()
                if key_text:
                    # if a key is found it returns it
                    return key_text
        
        # if not, prompts the user for it
        key = simpledialog.askstring(
            "Valid Google API Key Required",
            "Enter your Google API key \n Other LLM options not yet available"
        )
            
        # writes the key into file 
        if key:
            with open(KEY_FILE, "w") as f:
                f.write(key.strip())
            return key
        
        # if the user cancels the prompt, it returns None which will cause the verifier to fail and prompt the user again
        return None


# function to verify the API key
def verify_api_key_main():
    # reads the api key from the file and sets it as an environment variable for ADK
    api_key = get_or_request_api()
    os.environ["GOOGLE_API_KEY"] = api_key
    # creates an instance of the APIVerifier class and calls the verify_api_key() method
    verifier = APIVerifier(api_key)
    verification = verifier.verify_api_key()
    # deletes the verifier instance to free up memory
    del verifier
    # if the verification is successful, it prints a success message, otherwise it prompts the user for a new key and recalls itself
    if verification == True:
        print("API key successfully verified!")
    else:
        _error(verification)
        prompt_api_key()

# starts the verification process and after successful verification, it starts the main function
verify_api_key_main()
if __name__ == "__main__":
    main()
