import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import os
from pathlib import Path
from datetime import datetime
import threading
from google.genai import types
import asyncio
import json
import platform

if platform.system() == "Windows":
    from tkinter import Button as OSButton
else:
    from tkmacosx import Button as OSButton

# File directories
if platform.system() == "Windows":
    DATA_DIR = os.path.join(os.getenv("LOCALAPPDATA"),"Calispera")
    DATA_DIR_PROJECT = os.path.join(DATA_DIR,"AITAI")
else:
    DATA_DIR = os.path.join(os.path.join(Path.home(),"Documents"),"Calispera")
    DATA_DIR_PROJECT = os.path.join(DATA_DIR,"AITAI")

PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
# KEY_FILE = os.path.join(DATA_DIR, ".ai_api_key")
CHATS_FOLDER  = os.path.join(DATA_DIR_PROJECT, "chats")



# the AIChatApp class is responsible for the main app window and the pop up window on closing
class AIChatApp:
    def __init__(self, root,session_id, ui_history,agent_main, _save_and_exit):
        # startup tk stuff
        self.root = root
        self.root.title(f"AITAI: {session_id}")
        self.root.geometry("1080x840")
        self.root.configure(bg="#000000")

        # A thinking boolean which allows to send messages only after the agent finished responding or at the start of the conversation
        # A loading boolean which stops appending messages to the history while it loads them
        self.thinking = False
        self.loading = True
        # Gets the session_id from main.py which consists of the date,hours,minutes and seconds
        # Will later add chat saving and loading based on the dates
        self.session_id = session_id
        self.agent_main = agent_main
        print("Session ID: ", session_id)
        
        # Rows (Vertical space)
        self.root.grid_rowconfigure(0, weight=25) # Row 0 gets 58.8% of the Y axis
        self.root.grid_rowconfigure(1, weight=1) # Row 1 gets 5.8% of the Y axis
        self.root.grid_rowconfigure(2, weight=12) # Row 2 gets 29.4% of the Y axis
        self.root.grid_rowconfigure(3, weight=1) # Row 3 gets 5.8% of the Y axis

        # Columns (Horizontal space)
        self.root.grid_columnconfigure(0, weight=6) # Column 0 gets 66.6% of the X axis
        self.root.grid_columnconfigure(1, weight=2) # Column 1 gets 22.2% of the X axis
        self.session_path = os.path.join(CHATS_FOLDER, f"{self.session_id}.json")
        # Gets the history (empty if a new chat)
        self.ui_history = ui_history
        self._save_and_exit = _save_and_exit

        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        try:
            root.createcommand('::tk::mac::QuitScript', self.close_window)
        except Exception:
            pass
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
        # Loads chat from ui_history (if it's a new chat it won't do anything since ui_history starts as an empty list)
        for index,chat in enumerate(self.ui_history):
            if index == len(self.ui_history) - 1 and chat.get("role") == "user":
                # skip the last user message if it was not responded to
                continue
            if chat.get("role") == "user":
                self._append_to_chat("USER",chat.get("text"))
            elif chat.get("role") == "agent":
                self._append_to_chat("AGENT",chat.get("text"))
            elif chat.get("role") == "error":
                self._append_to_chat("ERROR",chat.get("text"))
            else:
                self._append_to_chat("SYSTEM",chat.get("text"))
        self.loading = False

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


        self.send_button = OSButton(
            self.input_frame, text="SEND", font=("Arial Bold", 13),
            bg="#FF6500", fg="white", borderwidth=0, cursor="hand2", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=5, ipadx=20)



        # ROW 2 (SUGGESTED ACTIONS)
        self.suggested_actions_frame = tk.Frame(self.root, bg="#07121F")
        self.suggested_actions_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
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

        self.accept_changes = OSButton(self.accept_changes_frame, text="Accept Changes", bg="#FF6500", fg="white", font=("Arial Bold", 12), borderwidth=0)
        self.accept_changes.pack(side = tk.LEFT, fill = tk.X, expand = True, padx = 5)



    def send_message(self):
        # Gets the message from the message entry object
        msg = self.message_entry.get("1.0", "end-1c").strip()
        if msg and self.thinking == False:
            # Adds the user message and also Agent is thinking to show that the message was received
            self._append_to_chat("USER",msg)
            self.message_entry.delete("1.0", "end")
            # Sets thinking to True so messages can't be sent during that time
            self.thinking = True
            self._append_to_chat("SYSTEM", "Agent is thinking...")
            try:
                # Starts a separate thread for sending the message to the agent and getting the response
                threading.Thread(target=self._send_to_agent, args=(msg,), daemon=True).start()
            except Exception as e:
                self._error(e)
    

    def _send_to_agent(self,user_text):
        # In case of error it will be put in the chatbox instead of the response 
        try:
            ai_reply = self.agent_main.generate_content(user_text)
            self.root.after(0, self._replace_thinking_with_response, "AGENT", ai_reply)
        except Exception as e:
            error_type = type(e).__name__
            raw_error_message = str(e)
            
            error_sender = "ERROR"
            formatted_message = f"[{error_type}] {raw_error_message}"
            # Adds a note if it looks like a quota issue
            if "quota" in raw_error_message.lower() or "429" in raw_error_message or "API returned no text" in raw_error_message:
                formatted_message += "\n\n(It looks like you ran out of Google API quota! Take a quick break and try again later.)"
            
            self.root.after(0,self._error,e)
            # Push the formatted error to the chat screen
            self.root.after(0, self._append_to_chat, error_sender, formatted_message)
            self.thinking = False

            
    
    def _replace_thinking_with_response(self, sender, message):
        # Deletes the Agent is thinking
        self.chat_history.config(state='normal')
        self.chat_history.delete("end-3l", "end-1c")
        self.chat_history.config(state='disabled')
        # Adds the message
        self._append_to_chat(sender, message)
        
        # Sets thinking to False so the user can send another message
        self.thinking = False
        self.message_entry.focus_set()
    
    def _append_to_chat(self,sender,message):
        # Inserts the message
        self.chat_history.config(state='normal')
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.see("end")
        self.chat_history.config(state='disabled')
        # If the chat isn't loading from startup adds to ui_history to save when closing
        if not self.loading:
            if sender == "USER":
                self.ui_history.append({"role":"user", "text": message})   
            elif sender == "AGENT":
                self.ui_history.append({"role":"agent", "text": message})
            elif sender == "SYSTEM":
                if not message == "Agent is thinking...":
                    self.ui_history.append({"role":"system", "text": message})
            elif sender == "ERROR":
                self.ui_history.append({"role":"error", "text": message})
    
    def _error(self,e):
        error_win  = tk.Toplevel(self.root)
        error_win.configure(bg="#07121F")

        error_win.transient(self.root) 
        error_win.grab_set()

        # prompts an error box 
        if hasattr(e, "code"):
            error_win.title(f"Error Code: {e.code}")
        else:
            error_win.title("Error")
        msg_label = tk.Label(error_win, text=str(e),bg = "#07121F", fg="#FF6500", wraplength=300)
        msg_label.pack(padx=20, pady=20)

    # Makes a new window to ask if to save, cancel or to not save the current chat
    def close_window(self):
        if self.thinking:
            return 0
        print("closing")
        self.root.focus_force()
        self.root.grab_release()

        dialogWindow = tk.Toplevel(self.root)
        dialogWindow.title("Exit")
        dialogWindow.geometry("500x170")
        dialogWindow.configure(bg="#07121F")

        dialogWindow.transient(self.root)
        dialogWindow.grab_set()
        dialogWindow.focus_set()

        tk.Label(dialogWindow, bg = "#07121F",fg = "white", font = ("Arial Bold",12), text="Do you want to save your chat before exiting?", pady=20).pack()

        def _exit_without_saving(self):
            # kills the whole app as it is
            dialogWindow.destroy()
            self.root.destroy() 

        btn_frame = tk.Frame(dialogWindow, bg = "#07121F")
        btn_frame.pack(pady = 20)
                
        btn_wdth = 10
        if platform.system() == "Windows":
            btn_wdth = 1

        # Button "Yes" calls the _save_and_exit function from main which handles the saving
        OSButton(btn_frame, text="Yes", bg="#FF6500", fg="white", font=("Arial Bold", 12), borderwidth=0, width = 15 * btn_wdth, cursor="hand2", command = self._save_and_exit).pack( side = tk.LEFT,padx = 20)
        # Button "Cancel" deletes the pop up window, letting the app itself open
        OSButton(btn_frame, text="Cancel", bg="#1E3E62", fg="white", font=("Arial Bold", 12), borderwidth=0, width = 10 * btn_wdth,  cursor="hand2", command = dialogWindow.destroy).pack( side = tk.LEFT)
        # Button "No" calls the _exit_without_saving function found above
        OSButton(btn_frame, text="No", bg="#1E3E62", fg="white", font=("Arial Bold", 12), borderwidth=0, width = 15 * btn_wdth, cursor="hand2", command= lambda: _exit_without_saving(self)).pack( side = tk.LEFT, padx = 20)




# The Picker class is responsible for the launcher window
class Picker:
    def __init__(self,launcher,existing_files,load_chat,create_new_chat):
        self.existing_files = existing_files
        self.result = {"session_id": None, "filepath": None}    
        self.launcher = launcher
        self.load_chat = load_chat
        self.create_new_chat = create_new_chat
        self.launcher.title("AITAI Launcher")
        self.launcher.geometry("450x500")
        self.launcher.configure(bg="#07121F")   

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.launcher, text="Select an Existing Workspace:", bg="#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=(20, 5))

        # Create a frame to hold the list and scrollbar
        list_frame = tk.Frame(self.launcher, bg="#07121F")
        list_frame.pack(fill="both", expand=True, padx=30, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.chat_listbox = tk.Listbox(list_frame, font=("Arial", 12), bg="#0B192C", fg="white", selectbackground="#FF6500", borderwidth=0, yscrollcommand=scrollbar.set)
        self.chat_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.chat_listbox.yview)
        
        for f in self.existing_files:
            # Remove the .json extension
            self.chat_listbox.insert(tk.END, f.replace(".json", ""))

        OSButton(self.launcher, text="Load Workspace", bg="#1E3E62", fg="white", font=("Arial Bold", 12), borderwidth=0, cursor="hand2", command=self.on_load_click).pack(pady=(5, 20), ipadx=10, ipady=5)


        tk.Frame(self.launcher, bg="#1E3E62", height=2).pack(fill="x", padx=30, pady=10)

        tk.Label(self.launcher, text="Or Create a New Workspace:", bg="#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=(10, 5))

        self.new_name_entry = tk.Entry(self.launcher, font=("Arial", 12), bg="#0B192C", fg="white", borderwidth=0, insertbackground="white")
        self.new_name_entry.pack(fill="x", padx=30, pady=5, ipady=5)
        self.new_name_entry.insert(0, "e.g., housing_analysis")

        self.new_name_entry.bind("<FocusIn>", self.clear_placeholder)

        OSButton(self.launcher, text="Create New", bg="#FF6500", fg="white", font=("Arial Bold", 12), borderwidth=0, cursor="hand2", command=self.on_create_click).pack(pady=(5, 30), ipadx=20, ipady=5)

    def on_load_click(self):
        session_id = None
        selection = self.chat_listbox.curselection()
        if selection:
            session_id = self.chat_listbox.get(selection[0])
            session_path = os.path.join(CHATS_FOLDER, f"{session_id}.json")

            self.load_chat(session_id, session_path)
            self.launcher.destroy() # Close the launcher
        else:
            messagebox.showwarning("Oops", "Please select a chat from the list first!", parent=self.launcher)

    def clear_placeholder(self, event):
        if self.new_name_entry.get() == "e.g., housing_analysis":
            self.new_name_entry.delete(0, tk.END)
    
    def on_create_click(self):
        session_id = None
        # Triggered when the user clicks 'Create New'
        raw_name = self.new_name_entry.get()
        file_name = raw_name + ".json"
        if file_name in self.existing_files:
            messagebox.showwarning("Warning","This file exists already\nConsider changing the name of your workspace or renaming the existing file")
        else:     
            # If they left it blank or didn't change the placeholder, use a timestamp
            if raw_name.strip() == "" or raw_name == "e.g., housing_analysis":
                session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            else:
                # Clean weird characters
                session_id = "".join([c for c in raw_name if c.isalnum() or c in (' ', '-', '_')]).strip()

            self.create_new_chat(session_id)
            # decided to NOT start an empty file from the start
            # json_file = open(result["filepath"], "w", encoding="utf-8")
            self.launcher.destroy() # Close the launcher