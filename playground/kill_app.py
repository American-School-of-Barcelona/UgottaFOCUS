import subprocess

def kill_app_by_name(app_name):
    """
    Use pkill to kill an application by process name.
    Simpler than finding PID first, still forceful.
    
    Args:
        app_name (str): Name of the application to kill (e.g., "Steam", "Discord")
    
    Returns:
        bool: True if app was found and killed, False if not running
    """
    try:
        result = subprocess.run(
            ['pkill', '-9', app_name],
            capture_output=True,
            text=True
        )
        
        # pkill returns 0 if it found and killed something
        # returns 1 if no matching processes found
        if result.returncode == 0:
            print(f"{app_name} terminated")
            return True
        else:
            print(f"{app_name} not running")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False