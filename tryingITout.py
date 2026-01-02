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

def open_blocklist_window():
    block_win = tk.Toplevel()
    block_win.title("Create Block List")
    block_win.geometry("500x500")

    notebook = ttk.Notebook(block_win)
    notebook.pack(fill='both', expand=True)

    
    apps_frame = tk.Frame(notebook)
    notebook.add(apps_frame, text="Applications")

    apps_list = get_installed_apps()
    apps_var_list = []

    canvas = tk.Canvas(apps_frame)
    scrollbar = tk.Scrollbar(apps_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for app in apps_list:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(scroll_frame, text=app, variable=var)
        chk.pack(anchor="w")
        apps_var_list.append((app, var))

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    
    site_frame = tk.Frame(notebook)
    notebook.add(site_frame, text="Websites")

    suggestions = [
        "youtube.com", "instagram.com", "tiktok.com",
        "discord.com", "netflix.com", "pinterest.com"
    ]
    site_vars = []

    tk.Label(site_frame, text="Suggested Websites:").pack(anchor="w")

    for site in suggestions:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(site_frame, text=site, variable=var)
        chk.pack(anchor="w")
        site_vars.append((site, var))

    tk.Label(site_frame, text="\nAdd custom websites:").pack(anchor="w")
    custom_entry = tk.Entry(site_frame, width=40)
    custom_entry.pack(anchor="w")

    def save_blocklist():
        BLOCKLIST_APPS.clear()
        BLOCKLIST_WEBSITES.clear()

        for app, var in apps_var_list:
            if var.get():
                BLOCKLIST_APPS.append(app)

        for site, var in site_vars:
            if var.get():
                BLOCKLIST_WEBSITES.append(site)

        custom_site = custom_entry.get().strip()
        if custom_site and "." in custom_site:
            BLOCKLIST_WEBSITES.append(custom_site)

        messagebox.showinfo("Saved", "Block list created!")

    tk.Button(block_win, text="Save Block List", command=save_blocklist).pack(pady=10)

#The actual window of the application
root = tk.Tk()
root.title("UgottaFOCUS")
root.geometry("400x300")

tk.Label(root, text="UgottaFOCUS", font=("Arial", 24)).pack(pady=20)

tk.Button(root, text="Create Block List", font=("Arial", 16), command=open_blocklist_window).pack(pady=10)
tk.Button(root, text="Start Focus Session", font=("Arial", 16), command=start_focus_session).pack(pady=10)
tk.Button(root, text="Quit", font=("Arial", 16), command=root.destroy).pack(pady=10)

root.mainloop()
