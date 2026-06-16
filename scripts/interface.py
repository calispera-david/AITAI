import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import os
from pathlib import Path

# File to store the API key locally
PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
# Saves the file in the user's directory under the folder "Calispera"
# KEY_FILE = os.path.join(os.path.join(Path.home(), "Calispera"),".ai_api_key")
print(KEY_FILE)

class AIChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Window 0.1")
        self.root.geometry("900x600")
        self.root.configure(bg = "#04030D")

        # Check for API Key inside ".ai_api_key" file
        self.api_key = self.get_or_request_api_key()
        if not self.api_key:
            messagebox.showerror("Error", "An API key is required to use this app.")
            self.root.destroy()
            return

        # Builds the application window
        self.setup_ui()

    def get_or_request_api_key(self):
        # Checks for a saved API key
        print(os.path.dirname(__file__))
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                apiKey = f.read().strip()
                if(apiKey): return apiKey
        
        # If no file is found or if empty, request it from the user via a popup
        key = simpledialog.askstring("API Key Required", "No API key found locally.\nPlease enter your API key:")
        if key:
            # Save the key for next time
            with open(KEY_FILE, "w") as f:
                f.write(key.strip())
            return key.strip()
        return None

    def setup_ui(self):
        # Handles the Window UI setup

        # Main window frame
        self.main_container = tk.PanedWindow(self.root, orient = tk.HORIZONTAL, bg = "#04030D",sashrelief = tk.FLAT, sashwidth = 6)
        self.main_container.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)

        # -----------------LEFT PANEL
        self.left_panel = tk.Frame(self.main_container, bg = "#04030D")

        # Chat History Area
        self.chat_history = scrolledtext.ScrolledText(self.left_panel, wrap=tk.WORD, bg = "#04030D",state='disabled', font=("Arial", 11))
        self.chat_history.pack( fill=tk.BOTH, expand=True)


        self.chat_history.tag_config("UserColor", foreground="#8ab4f8")   # Light Blue
        self.chat_history.tag_config("AgentColor", foreground="#81c995")  # Light Green
        self.chat_history.tag_config("SystemColor", foreground="#ffffff") # Yellow
        self.chat_history.tag_config("BoldText", font=("Arial", 11, "bold"))

        # Frame for message box and send button
        self.input_frame = tk.Frame(self.left_panel, bg = "#04030D")
        self.input_frame.pack(fill=tk.X)

        # Message Input Box
        self.message_entry = tk.Entry(self.input_frame, font=("Arial", 12))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        # Allow hitting Return to send instead of using the button
        self.message_entry.bind("<Return>", self.send_message) 

        # Send Button
        self.send_button = tk.Button(self.input_frame, text="Send", bg = "#2F2FE4", fg = "white", command=self.send_message, width=8)
        self.send_button.pack(side=tk.RIGHT)

        self.main_container.add(self.left_panel, stretch="always", minsize=300)

        # ---------------RIGHT PANEL
        self.right_panel = tk.Frame(self.main_container, bg = "#04030D")

        self.changes_label = tk.Label(
            self.right_panel, text="Changes", 
            bg="#04030D", fg="#B7B5FF", font=("Arial Bold", 20)
        )
        self.changes_label.pack(pady=20)

        self.main_container.add(self.right_panel, stretch="always", minsize=150)
        # Initial Welcome Message
        self.append_to_chat("v0.1", "Welcome! Start chatting with your AI agent or type /help for a quick guide. \n DISCLAIMER: This app is a work in progress and may not work as expected.")

    def send_message(self, event=None):
        # Handles sending the user's message
        user_text = self.message_entry.get().strip()
        if not user_text:
            return # Don't send empty messages

        # Display user message and clear input
        self.append_to_chat("User", user_text)
        self.message_entry.delete(0, tk.END)

        # TO DO: Send the user input to "agent.py" and get the response
        
        # Simulating an AI response for demonstration
        self.root.after(500, lambda: self.append_to_chat("AI", f"This is a placeholder response to: '{user_text}'"))

    def append_to_chat(self, sender, message):
        """Safely adds a new message to the chat history."""
        self.chat_history.config(state='normal') # Temporarily enable to insert text

        if sender == "User":
            color_tag = "UserColor"
        elif sender in ["Agent", "AI", "Gemini"]:
            color_tag = "AgentColor"
        else:
            color_tag = "SystemColor" # For "System" or "Error" messages

        # 2. Insert the Sender Name
        # We can apply MULTIPLE tags by passing them as a tuple: ("BoldText", color_tag)
        self.chat_history.insert(tk.END, f"{sender}: ", ("BoldText", color_tag))
        self.chat_history.insert(tk.END, f"{message}\n\n", "SystemColor")
        
        self.chat_history.see(tk.END) # Auto-scroll to the bottom
        self.chat_history.config(state='disabled') # Disable to prevent user typing in history

if __name__ == "__main__":
    root = tk.Tk()
    app = AIChatApp(root)
    root.mainloop()