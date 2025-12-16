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
    focus_running = True
    end_time = time.time() + duration_minutes * 60

    while time.time() < end_time and focus_running:

        for app in BLOCKLIST_APPS:
            kill_app_by_name(app)

        tabs = getCurrentChromeTabs()
        for tab in tabs:
            url = tab["url"]
            if any(site in url for site in BLOCKLIST_WEBSITES):
                closeChromeTab(url, tab["window"])

        time.sleep(1)

    focus_running = False
    show_session_summary()

def closeChromeTab(url, window_index):
    script = f'''
    tell application "Google Chrome"
        tell window {window_index}
            repeat with t in tabs
                if (URL of t) is "{url}" then close t
            end repeat
        end tell
    end tell
    '''
    os.system(f"osascript -e '{script}'")

def show_session_summary():
    history = getRecentChromeHistoryCopy(limit=20)

    recent_distractions = [
        entry for entry in history
        if any(site in entry["url"] for site in BLOCKLIST_WEBSITES)
    ]

    summary = f"Blocked apps: {len(BLOCKLIST_APPS)}\n"
    summary += f"Blocked websites: {len(BLOCKLIST_WEBSITES)}\n"
    summary += f"Recent distractions: {len(recent_distractions)}\n\n"

    if recent_distractions:
        summary += "Recent Distraction URLs:\n"
        for item in recent_distractions:
            summary += "- " + item['url'] + "\n"

    messagebox.showinfo("Focus Session Summary", summary)

def start_focus_session():
    if not BLOCKLIST_APPS and not BLOCKLIST_WEBSITES:
        messagebox.showwarning("Error", "Please create a block list first!")
        return

    minutes = simpledialog.askinteger(
        "Focus Session",
        "How many minutes do you want to stay focused?",
        minvalue=1,
        maxvalue=300
    )

    if not minutes:
        return

    t = threading.Thread(target=block_loop, args=(minutes,))
    t.daemon = True
    t.start()

    messagebox.showinfo("Focus Started", "Focus session is now running!")

#The actual window of the application
root = tk.Tk()
root.title("UgottaFOCUS")
root.geometry("400x300")

tk.Label(root, text="UgottaFOCUS", font=("Arial", 24)).pack(pady=20)

tk.Button(root, text="Create Block List", font=("Arial", 16), command=open_blocklist_window).pack(pady=10)
tk.Button(root, text="Start Focus Session", font=("Arial", 16), command=start_focus_session).pack(pady=10)
tk.Button(root, text="Quit", font=("Arial", 16), command=root.destroy).pack(pady=10)

root.mainloop()
