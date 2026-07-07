from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from google.genai import types
from google import genai
import os
from pathlib import Path
import asyncio
import threading
import datetime
import json


from scripts.interface import AIChatApp
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

PROJECT_ROOT = Path(__file__).parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
CHATS_FOLDER  = os.path.join(PROJECT_ROOT, "chats")
os.makedirs(CHATS_FOLDER, exist_ok=True)



def _error(e):
    # prompts an error box 
    if hasattr(e, "code"):
        messagebox.showerror(f"Error Code: {e.code}", e.message)
    else:
        messagebox.showerror("Error", e)


            



def main():
    try:
        with open(KEY_FILE, "r") as f: 
            api_key =  f.read().strip()
        os.environ["GOOGLE_API_KEY"] = api_key
        print("api_key: ", api_key)
        os.environ["GOOGLE_API_KEY"] = api_key
        chat_memory = InMemorySessionService()
        chat_runner = Runner(agent = agent, session_service = chat_memory, app_name = "csv_analyzer")
        
        picker_result = chat_picker()
        session_id = picker_result[0]
        session = None
        if not (picker_result[0] == None or picker_result[1] == None):
            session = asyncio.run(chat_memory.create_session(
                app_name="csv_analyzer", 
                user_id="default_user", 
                session_id=session_id
            ))

            # starts the UI
            root = tk.Tk()
            app = AIChatApp(root, chat_runner, session_id, session)
            def _close_app():
                if app.thinking:
                    return 0
                print("closing")
                root.focus_force()
                history_to_save = []
                save_file_path = os.path.join(os.path.join(PROJECT_ROOT,"chats"),f"{session_id}.json")
                res = messagebox.askyesno("Exit", "Do you want to save your chat before you exit?")
                if res:
                    try:
                        
                        latest_session = asyncio.run(chat_memory.get_session(
                            app_name="csv_analyzer", 
                            user_id="default_user", 
                            session_id=session_id
                            ))

                        for event in latest_session.events:
                            print(event,"\n\n")
                            if hasattr(event, 'content') and event.content and event.content.parts:
                                history_to_save.append({
                                    "role": event.content.role,
                                    "text": event.content.parts[0].text
                                })
                        with open(save_file_path, "w") as f:
                            json.dump(history_to_save,f)
                        
                        root.destroy()
                        
                    except Exception as e:
                        _error(e)
                        res = messagebox.askyesno("Error", "Error while saving \nDo you want to exit without saving?")
                        if res:
                            root.destroy()
                else:
                    res = messagebox.askyesno("Exit", "Are you sure you don't want to save?")
                    if res:
                        root.destroy()
            root.protocol("WM_DELETE_WINDOW", _close_app)
            root.mainloop()
    except Exception as e:
        print("Initialization failed")
        print(e)

def prompt_api_key():
    key = simpledialog.askstring(
            "Valid Google API Key Required",
            "Enter your Google API key \n Other LLM options not yet available"
        )
            
    if key:
        with open(KEY_FILE, "w") as f:
            f.write(key.strip())
        verify_api_key()
    else:
        messagebox.showerror("Error", "A valid Google API key is required to use this app.")
    
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
        
        return None
def verify_api_key():
    api_key = ""
    api_key = get_or_request_api()
    os.environ["GOOGLE_API_KEY"] = api_key
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
        if hasattr(e, "code"):
            if e.code == 400:
                with open(KEY_FILE , 'w') as f:
                    f.write("".strip())
                # Prompts the user for the key
                prompt_api_key()
        exit()


# Custom launcher to laod or start new chats
def chat_picker():
    # Creates a Launcher Window
    result = {"session_id": None, "filepath": None}
    launcher = tk.Tk()
    launcher.title("AITAI Launcher")
    launcher.geometry("450x500")
    launcher.configure(bg="#07121F")

    tk.Label(launcher, text="Select an Existing Workspace:", bg="#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=(20, 5))

    # Create a frame to hold the list and scrollbar
    list_frame = tk.Frame(launcher, bg="#07121F")
    list_frame.pack(fill="both", expand=True, padx=30, pady=5)
    
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    
    chat_listbox = tk.Listbox(list_frame, font=("Arial", 12), bg="#0B192C", fg="white", selectbackground="#FF6500", borderwidth=0, yscrollcommand=scrollbar.set)
    chat_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=chat_listbox.yview)
    
    # Read the chats folder and populate the listbox
    existing_files = [f for f in os.listdir(CHATS_FOLDER) if f[-5:] == ".json"]
    for f in existing_files:
        # Remove the .json extension for a cleaner look
        chat_listbox.insert(tk.END, f.replace(".json", ""))

    

    ui_history = []
    def on_load_click():
        # Triggered when the user clicks 'Load Workspace'
        selection = chat_listbox.curselection()
        if selection:
            session_id = chat_listbox.get(selection[0])
            session_path = os.path.join(CHATS_FOLDER, f"{session_id}.json")

            result["session_id"] = session_id
            result["filepath"] = session_path
            launcher.destroy() # Close the launcher
        else:
            messagebox.showwarning("Oops", "Please select a chat from the list first!", parent=launcher)
    
    tk.Button(launcher, text="Load Workspace", bg="#1E3E62", fg="white", font=("Arial Bold", 12), borderwidth=0, cursor="hand2", command=on_load_click).pack(pady=(5, 20), ipadx=10, ipady=5)

    tk.Frame(launcher, bg="#1E3E62", height=2).pack(fill="x", padx=30, pady=10)

    tk.Label(launcher, text="Or Create a New Workspace:", bg="#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=(10, 5))

    new_name_entry = tk.Entry(launcher, font=("Arial", 12), bg="#0B192C", fg="white", borderwidth=0, insertbackground="white")
    new_name_entry.pack(fill="x", padx=30, pady=5, ipady=5)
    new_name_entry.insert(0, "e.g., housing_analysis")

    def clear_placeholder(event):
        if new_name_entry.get() == "e.g., housing_analysis":
            new_name_entry.delete(0, tk.END)
    
    new_name_entry.bind("<FocusIn>", clear_placeholder)
    def on_create_click():
        # Triggered when the user clicks 'Create New'
        raw_name = new_name_entry.get()
        file_name = raw_name + ".json"
        if file_name in existing_files:
            messagebox.showwarning("Warning","This file exists already\nConsider changing the name of your workspace or renaming the existing file")
            return None
            
        # If they left it blank or didn't change the placeholder, use a timestamp
        if raw_name.strip() == "" or raw_name == "e.g., housing_analysis":
            session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            # Clean weird characters
            session_id = "".join([c for c in raw_name if c.isalnum() or c in (' ', '-', '_')]).strip()
            
        result["session_id"] = session_id
        result["filepath"] = os.path.join(CHATS_FOLDER, f"{session_id}.json")
        # decided to NOT start an empty file from the start
        # json_file = open(result["filepath"], "w", encoding="utf-8")
        launcher.destroy() # Close the launcher

    tk.Button(launcher, text="Create New", bg="#FF6500", fg="white", font=("Arial Bold", 12), borderwidth=0, cursor="hand2", command=on_create_click).pack(pady=(5, 30), ipadx=20, ipady=5)

    # 2. Tell Python to pause the script here until the launcher window is closed
    launcher.wait_window()

    return result["session_id"], result["filepath"]



# verify_api_key()
from agent.agent import agent
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
