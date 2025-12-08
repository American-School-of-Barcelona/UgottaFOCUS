import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
import time
from chromeCheck import getCurrentChromeTabs
from kill_app import kill_app_by_name
from chromeHistory import getRecentChromeHistoryCopy
import os
import json

TK_SILENCE_DEPRECATION=1

BLOCKLIST_APPS=[]
BLOCKLIST_WEBSITES=[]
focus_running=False

def get_installed_apps():
    apps_dir="/Applications"
    apps=[]

    if not os.path.exists(apps_dir):
        return apps

    for item in os.listdir(apps_dir):
        if item.endswith(".app"):
            apps.append(item.replace(".app",""))

    return sorted(apps)
