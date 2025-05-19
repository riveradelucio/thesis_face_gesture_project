from app.role_identifier import get_user_role
from app.text_to_speech import speak_text
import threading  # ✅ new

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
    thread.start()

def greet_user_by_role(name: str):
    role = get_user_role(name)
    name_clean = name.capitalize()

    greeting = f"Hello {name_clean}, you are recognized as a {role}."

    if role == "Elderly user":
        greeting += " It's nice to see you today. I hope you're feeling well."
    elif role == "Family member":
        greeting += " Welcome back. It’s good to have you here."
    elif role == "Caregiver":
        greeting += " Thanks for taking care. Let me know if you need help."

    speak_in_background(greeting)  # ✅ background speaking
