from pathlib import Path
import os
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import datetime
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHATS_FOLDER  = os.path.join(PROJECT_ROOT, "chats")
os.makedirs(CHATS_FOLDER, exist_ok=True)

