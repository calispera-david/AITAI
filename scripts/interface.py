import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import os
from pathlib import Path
import datetime
import threading
from google.genai import types
import asyncio
import json

# File to store the API key locally
PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
CHATS_FOLDER  = os.path.join(PROJECT_ROOT, "chats")


# KEY_FILE = os.path.join(os.path.join(Path.home(), "Calispera"),".ai_api_key")
# CHATS_FOLDER  = os.path.join(os.path.join(Path.home(), "Calispera"),"chats")


class AIChatApp:
    def __init__(self, root, chat_runner,session_id,session):
        # startup tk stuff
        self.root = root
        self.root.title(f"AITAI: {session_id}")
        self.root.geometry("1080x840")
        self.root.configure(bg="#000000")
        # gets the chat_runner from main.py which initializes a session
        self.chat_runner = chat_runner
        # A thinking boolean which allows to send messages only after the agent finished responding or at the start of the conversation
        self.thinking = False
        # Gets the session_id from main.py which consists of the date,hours,minutes and seconds
        # Will later add chat saving and loading based on the dates
        self.session_id = session_id
        self.session = session
        print("Session ID: ", session_id)
        
        # Self explanatory, if the api file is not found it prompts for one
        self.api_key = self.get_or_request_api()
        if not self.api_key:
            # If the user doesn't input any text
            messagebox.showerror("Error", "A valid Google API key is required to use this app.")
            self.root.destroy()
            return

        # Rows (Vertical space)
        self.root.grid_rowconfigure(0, weight=25) # Row 0 gets 58.8% of the Y axis
        self.root.grid_rowconfigure(1, weight=1) # Row 1 gets 5.8% of the Y axis
        self.root.grid_rowconfigure(2, weight=12) # Row 2 gets 29.4% of the Y axis
        self.root.grid_rowconfigure(3, weight=1) # Row 3 gets 5.8% of the Y axis

        # Columns (Horizontal space)
        self.root.grid_columnconfigure(0, weight=6) # Column 0 gets 66.6% of the X axis
        self.root.grid_columnconfigure(1, weight=2) # Column 1 gets 22.2% of the X axis
        self.ui_history = []
        self.session_path = os.path.join(CHATS_FOLDER, f"{self.session_id}.json")
        if os.path.exists(self.session_path):
            try:
                with open(self.session_path,"r") as f:
                    self.ui_history = json.load(f)
            except Exception as e:
                self._error(e)
                self._error("Chat found but can't be loaded\nTry again later.")
                exit()
        self.setup_ui()


    def setup_ui(self):
        # ROW 0 COL 0 (CHATBOX)
        self.chat_box_frame = tk.Frame(self.root, bg="#07121F")
        self.chat_box_frame.grid(row=0, column=0,sticky = "nsew", padx=10, pady=(10, 5))
        

        tk.Label(self.chat_box_frame, text="CHAT", bg = "#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=5)
        

        self.chat_history = scrolledtext.ScrolledText(
            self.chat_box_frame, wrap=tk.WORD, state='disabled',
            bg="#0B192C", fg="white", font=("Arial Bold", 12), borderwidth=0,
            width = 1, height = 1, padx = 5,pady = 5
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        for chat in self.ui_history:
            if chat.get("role") == "user":
                self._append_to_chat("USER",chat.get("text"))
            else:
                self._append_to_chat("AGENT",chat.get("text"))
        

        # ROW 0 COL 1 (CHANGE HISTORY)
        self.change_history_frame = tk.Frame(self.root, bg="#07121F")
        self.change_history_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 5))


        tk.Label(self.change_history_frame, text="CHANGE HISTORY", bg="#07121F", fg="#A0AAB5", font=("Arial Bold", 14)).pack(pady=5)
        

        self.change_history = scrolledtext.ScrolledText(
            self.change_history_frame, wrap=tk.WORD, state='disabled',
            bg="#0B192C", fg="#A0AAB5", font=("Arial", 10), borderwidth=0,
            width = 1, height = 1
        )
        self.change_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        


        # ROW 1 COL 0-1 (INPUT)
        self.input_frame = tk.Frame(self.root, bg = "#07121F")
        self.input_frame.grid(row = 1, column = 0, columnspan = 2, sticky = "nsew", padx = 10, pady = 5)


        self.message_entry = tk.Text(
            self.input_frame, font=("Arial", 12), wrap="word", height=2,
            bg="#1E3E62", fg="white", insertbackground="white", borderwidth=0,
            padx = 5, pady = 5
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Removed the ability to send using enter in order to be able to make new lines
        # self.message_entry.bind("<Return>", self.send_message)


        self.send_button = tk.Button(
            self.input_frame, text="SEND", font=("Arial Bold", 13),
            bg="#FF6500", fg="white", borderwidth=0, cursor="hand2", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=5, ipadx=20)



        # ROW 2 (SUGGESTED ACTIONS)
        self.suggested_actions_frame = tk.Frame(self.root, bg="#07121F")
        self.suggested_actions_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        # grid_propagate(False) forces the frame to stay 120px tall, instead of shrinking to wrap the text inside it
        self.suggested_actions_frame.grid_propagate(False) 
        

        tk.Label(self.suggested_actions_frame, text="SUGGESTED ACTIONS", bg="#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=5)


        self.suggested_actions = scrolledtext.ScrolledText(
            self.suggested_actions_frame, wrap=tk.WORD, state='disabled',
            bg="#0B192C", fg="#A0AAB5", font=("Arial", 10), borderwidth=0, 
            width = 1, height = 1
        )
        self.suggested_actions.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))



        # ROW 3 (ACCEPT CHANGES)
        self.accept_changes_frame = tk.Frame(self.root, bg = "#07121F")
        self.accept_changes_frame.grid(row = 3, column = 0, columnspan = 2, sticky = "nsew", padx = 10, pady = (5,10))

        self.accept_changes = tk.Button(self.accept_changes_frame, text="Accept Changes", bg="#FF6500", fg="white", font=("Arial Bold", 12), borderwidth=0)
        self.accept_changes.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = 5)


    def get_or_request_api(self):
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


    def send_message(self):
        msg = self.message_entry.get("1.0", "end-1c").strip()
        if msg and self.thinking == False:
            self._append_to_chat("USER",msg)

            self.message_entry.delete("1.0", "end")
            self.thinking = True

            self._append_to_chat("SYSTEM", "Agent is thinking...")
            try:
                threading.Thread(target=self._send_to_agent, args=(msg,), daemon=True).start()
            except Exception as e:
                _error(e)
    

    def _send_to_agent(self,user_text):
        try:
            user_msg = types.Content(role="user", parts=[types.Part(text=user_text)])

            final_text = ""

            events = self.chat_runner.run(
                user_id="default_user",
                session_id= self.session_id, 
                new_message=user_msg
            )
            for event in events:

                print("\n--- RAW ADK EVENT ---")
                print(event)
                if hasattr(event, 'content') and event.content and event.content.parts:
                    final_text = event.content.parts[0].text
                    

                elif hasattr(event, 'error_code') and event.error_code:
                    error_details = getattr(event, 'error_message', 'Unknown API Error')
                    raise RuntimeError(f"{event.error_code} - {error_details}")
            if not final_text:
                raise ValueError("API returned no text. You likely hit a quota limit or safety block.")
            
            ai_reply = final_text
            self.root.after(0, self._replace_thinking_with_response, "Agent", ai_reply)

        except Exception as e:
            error_type = type(e).__name__
            raw_error_message = str(e)
            
            error_sender = "ERROR"
            formatted_message = f"[{error_type}] {raw_error_message}"
            
            # Add a friendly note if it smells like a quota issue
            if "quota" in raw_error_message.lower() or "429" in raw_error_message or "API returned no text" in raw_error_message:
                formatted_message += "\n\n(It looks like you ran out of Google API quota! Take a quick break and try again later.)"
                
            # Push the formatted error to the chat screen
            self.root.after(0, self._replace_thinking_with_response, error_sender, formatted_message)
            self._error(e)
            
    
    def _replace_thinking_with_response(self, sender, message):
        self.chat_history.config(state='normal')
        self.chat_history.delete("end-3l", "end-1c")
        self.chat_history.config(state='disabled')
        
        self._append_to_chat(sender, message)
        
        self.thinking = False
        self.message_entry.focus_set()
    
    def _append_to_chat(self,sender,message):
        self.chat_history.config(state='normal')
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.see("end")
        self.chat_history.config(state='disabled')
    
    def _error(self,e):
        # prompts an error box 
        if hasattr(e, "code"):
            messagebox.showerror(f"Error Code: {e.code}", e.message)
        else:
            messagebox.showerror("Error", e)

        
# root = tk.Tk()
# app = AIChatApp(root)
# root.mainloop()