# dumb_user_registration.py

import time
import threading
from datetime import datetime
import cv2
from app.text_to_speech import speak_text
from app.subtitle_manager import update_subtitle
from app.gesture_responder import overlay_centered_animation
from app.config import RAW_BACKGROUND
from app.screen_camera_and_subtitles import add_subtitles

def play_animation_during_speech(messages, cap, window_name, window_width, window_height):
    for msg in messages:
        update_subtitle(msg)
        start_time = time.time()

        def speak():
            speak_text(msg)

        tts_thread = threading.Thread(target=speak)
        tts_thread.start()

        while tts_thread.is_alive():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            background_frame = cv2.resize(RAW_BACKGROUND, (int(frame.shape[1] * 0.8), frame.shape[0]))
            animated_frame = overlay_centered_animation(background_frame.copy(), "Speaking", start_time, duration=3)
            frame_with_text = add_subtitles(animated_frame, msg)
            cv2.imshow(window_name, frame_with_text)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

def handle_dumb_user_registration(cap, window_name, window_width, window_height, last_known_user=None):
    """
    Dumb version of user registration. Asks for name and reminder time.
    The name and time are not stored permanently.
    """
    if last_known_user is None:
        intro1 = "Hi there! I am Luis. I do not know you yet. Your are to new user to me."
        intro2 = "Could you please type your name on the keyboard so we can get to know each other?"

        play_animation_during_speech([intro1, intro2], cap, window_name, window_width, window_height)

        name = input("Enter your name: ").strip().capitalize()

        ask_reminder = "At what time should I remind you to take your medication? Please type it as for example 3 PM or 08:30 AM."
        play_animation_during_speech([ask_reminder], cap, window_name, window_width, window_height)

        reminder_time = input("Enter your reminder time (e.g., 3 PM or 08:30 AM): ").strip()

        greeting = f"Hello {name}, it's nice to meet you."
    else:
        name = last_known_user
        reminder_time = "3 PM"  # fallback if not passed
        greeting = f"Welcome back {name}, it's good to see you again."

    time_info = time.strftime("The time is %I:%M %p").lstrip("0").lower()
    reminder = f"This is your daily reminder to take your medication at {reminder_time}."

    play_animation_during_speech([greeting, time_info, reminder], cap, window_name, window_width, window_height)

    return name
