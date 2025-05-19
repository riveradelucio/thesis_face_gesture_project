from app.role_identifier import get_user_role
from app.role_database import USER_ROLES
from app.text_to_speech import speak_text
from app.visit_logger import log_user_visit, user_visited_today, get_last_visit

import threading
from datetime import datetime

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
    thread.start()

def greet_user_by_role(name: str):
    role = get_user_role(name)
    name_clean = name.capitalize()

    first_visit = not user_visited_today(name)
    log_user_visit(name)

    greeting = f"Hello {name_clean}, you are recognized as a {role}."

    # 👨‍👩‍👧 Mention elderly user's last visit if this is a family member or caregiver
    if role in ["Family member", "Caregiver"]:
        elderly_users = [user for user, r in USER_ROLES.items() if r == "Elderly user"]
        if elderly_users:
            elderly_name = elderly_users[0].capitalize()
            last_seen_time = get_last_visit(elderly_users[0])
            if last_seen_time:
                hour = last_seen_time.hour
                if 5 <= hour < 12:
                    period = "morning"
                elif 12 <= hour < 18:
                    period = "afternoon"
                else:
                    period = "evening"

                time_str = last_seen_time.strftime("%I:%M %p").lstrip("0")
                greeting += f" Last time I saw {elderly_name} was in the {period} at {time_str.lower()}."

    # 🧓 Elderly-specific phrasing
    if role == "Elderly user":
        if first_visit:
            greeting += " It's nice to see you today. I hope you're feeling well."
        else:
            greeting = f"Welcome back {name_clean}, it's good to see you again."

    # 🖐️ Add natural transition to gesture mode
    gesture_prompt = "Let me know how I can help, just show me a hand gesture."
    full_message = f"{greeting} {gesture_prompt}"

    speak_in_background(full_message)
