from app.role_identifier import get_user_role
from app.text_to_speech import speak_text
from app.visit_logger import log_user_visit, user_visited_today
import threading

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
    thread.start()

def greet_user_by_role(name: str):
    role = get_user_role(name)
    name_clean = name.capitalize()

    first_visit = not user_visited_today(name)  # ✅ Check if user already visited today
    log_user_visit(name)                        # ✅ Log the current visit

    if first_visit:
        greeting = f"Hello {name_clean}, you are recognized as a {role}."
        if role == "Elderly user":
            greeting += " It's nice to see you today. I hope you're feeling well."
        elif role == "Family member":
            greeting += " Welcome! Thanks for coming today."
        elif role == "Caregiver":
            greeting += " Thank you for your work. Let me know if you need assistance."
    else:
        greeting = f"Welcome back {name_clean}, our {role.lower()}."

    speak_in_background(greeting)
