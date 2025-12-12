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


def block_loop(duration_minutes):
    global focus_running
    focus_running=True
    end_time=time.time()+duration_minutes*60

    while time.time()<end_time and focus_running:

        for app in BLOCKLIST_APPS:
            kill_app_by_name(app)

        tabs=getCurrentChromeTabs()
        for tab in tabs:
            url=tab["url"]
            if any(site in url for site in BLOCKLIST_WEBSITES):
                closeChromeTab(url,tab["window"])

    focus_running=False
