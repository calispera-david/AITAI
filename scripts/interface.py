import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import os
from pathlib import Path

# File to store the API key locally
PROJECT_ROOT = Path(__file__).parent.parent
KEY_FILE = os.path.join(PROJECT_ROOT, ".ai_api_key")
# Saves the file in the user's directory under the folder "Calispera"
# KEY_FILE = os.path.join(os.path.join(Path.home(), "Calispera"),".ai_api_key")


class AIChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Window")
        self.root.geometry("1080x840")
        self.root.configure(bg="#000000")
        
        
        # Rows (Vertical space)
        self.root.grid_rowconfigure(0, weight=25) # Row 0 gets 58.8% of the Y axis
        self.root.grid_rowconfigure(1, weight=1) # Row 1 gets 5.8% of the Y axis
        self.root.grid_rowconfigure(2, weight=12) # Row 2 gets 29.4% of the Y axis
        self.root.grid_rowconfigure(3, weight=1) # Row 3 gets 5.8% of the Y axis

        # Columns (Horizontal space)
        self.root.grid_columnconfigure(0, weight=6) # Column 0 gets 66.6% of the X axis
        self.root.grid_columnconfigure(1, weight=2) # Column 1 gets 22.2% of the X axis

        self.setup_ui()

    def setup_ui(self):
        # ROW 0 COL 0 (CHATBOX)
        self.chat_box_frame = tk.Frame(self.root, bg="#07121F")
        self.chat_box_frame.grid(row=0, column=0,sticky = "nsew", padx=10, pady=(10, 5))
        

        tk.Label(self.chat_box_frame, text="CHAT", bg = "#07121F", fg="white", font=("Arial Bold", 14)).pack(pady=5)
        

        self.chat_history = scrolledtext.ScrolledText(
            self.chat_box_frame, wrap=tk.WORD, state='disabled',
            bg="#0B192C", fg="white", font=("Arial", 12), borderwidth=0,
            width = 1, height = 1
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        

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
            bg="#1E3E62", fg="white", insertbackground="white", borderwidth=0
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.message_entry.bind("<Return>", self.send_message)


        self.send_button = tk.Button(
            self.input_frame, text="SEND", font=("Arial Bold", 13),
            bg="#FF6500", fg="white", borderwidth=0, cursor="hand2", command=self.send_message
        )
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

    def send_message(msg):
        print("message sent to the agent")
if __name__ == "__main__":
    root = tk.Tk()
    app = AIChatApp(root)
    root.mainloop()