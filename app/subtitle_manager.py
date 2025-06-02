import time

# Global variables for tracking subtitle state
current_subtitle = ""
last_update_time = 0
subtitle_display_duration = 10  # seconds

def update_subtitle(text):
    """
    Update the subtitle with new text and reset the timer.
    """
    global current_subtitle, last_update_time
    current_subtitle = text
    last_update_time = time.time()

def get_current_subtitle():
    """
    Return the current subtitle if it's still within the display duration.
    Otherwise, return an empty string.
    """
    if time.time() - last_update_time < subtitle_display_duration:
        return current_subtitle
    return ""
