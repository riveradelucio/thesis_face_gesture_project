# dumb_user_registration.py

import time
from app.text_to_speech import speak_text
from app.subtitle_manager import update_subtitle

def handle_dumb_user_registration():
    """
    Dumb version of user registration. Only asks for a name and speaks back.
    The name is not saved.
    """
    # Intro message (blocking, same as smart version)
    intro1 = "Hi there! I am Luis. I do not recognize you yet. Your face is new to me."
    intro2 = "Could you please type your name on the keyboard so we can get to know each other?"

    update_subtitle(intro1)
    speak_text(intro1)
    time.sleep(0.3)
    update_subtitle(intro2)
    speak_text(intro2)

    name = input("Enter your name: ").strip().capitalize()

    # Greeting and fixed reminder (also blocking for subtitle sync)
    greeting = f"Hello {name}, it's nice to meet you."
    time_info = time.strftime("The time is %I:%M %p").lstrip("0").lower()
    reminder = "This is your daily reminder to take your medication at 3 PM."

    update_subtitle(greeting)
    speak_text(greeting)
    time.sleep(0.3)
    update_subtitle(time_info)
    speak_text(time_info)
    time.sleep(0.3)
    update_subtitle(reminder)
    speak_text(reminder)
