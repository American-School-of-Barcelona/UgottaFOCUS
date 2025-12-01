import subprocess

def close_app_gracefully(app_name):
    """
    Use AppleScript to quit an application gracefully (like clicking Quit).
    This allows the app to save state and shut down cleanly.
    
    Args:
        app_name (str): Name of the application to close (e.g., "Steam", "Discord")
    
    Returns:
        bool: True if successful, False otherwise
    """
    applescript = f'''
    tell application "System Events"
        if exists (process "{app_name}") then
            tell application "{app_name}" to quit
            return "{app_name} closed"
        else
            return "{app_name} not running"
        end if
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout.strip())
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False