# new_user_registration.py

import os
import cv2
import threading
import time

from app.role_database import USER_ROLES, save_roles
from app.face_recognition import register_known_faces
from app.text_to_speech import speak_text
from app.subtitle_manager import update_subtitle

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
    thread.start()

def speak_multiple_lines_in_background(lines, delay=0.3):
    def run():
        for line in lines:
            update_subtitle(line)
            speak_text(line)
            time.sleep(delay)
    thread = threading.Thread(target=run)
    thread.start()

def save_new_face_image(_, name):
    speak_in_background("Could you stay still for a moment? I will take a picture of you.")
    time.sleep(5)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot access webcam to take picture.")
        return

    ret, fresh_frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture image.")
        return

    fresh_frame = cv2.flip(fresh_frame, 1)
    filename = os.path.join("known_faces", f"{name.lower()}.jpg")
    cv2.imwrite(filename, fresh_frame)
    print(f"✅ Image saved as {filename}")

def handle_new_user_registration(frame):
    print("Stage 1: Starting user registration")
    speak_multiple_lines_in_background([
        "Hi there! I am Luis. I do not recognize you yet. Your face is new to me.",
        "Could you please type your name and role on the keyboard so we can get to know each other?"
    ])

    print("Stage 2: Waiting for user input...")
    name = input("Enter name for new user: ").strip().lower()

    valid_roles = {
        "1": "Elderly user",
        "2": "Family member",
        "3": "Caregiver"
    }

    print("Select role for the new user:")
    for key, role in valid_roles.items():
        print(f"{key}. {role}")

    role_input = None
    while role_input not in valid_roles:
        role_input = input("Enter the number of the role (1–3): ").strip()

    role = valid_roles[role_input]
    print(f"✅ Name: {name}, Role: {role}")

    # ✅ Ask for reminder time
    speak_in_background("At what time should I remind you to take your medication? Please type it as for example 3 PM or 08:30 AM.")
    reminder_time = input("Enter your reminder time (e.g., 3 PM or 08:30 AM): ").strip()
    print(f"✅ Reminder time set to: {reminder_time}")

    save_new_face_image(frame, name)

    print("Stage 4: Saving role and updating face database...")
    USER_ROLES[name] = role
    save_roles(USER_ROLES)
    register_known_faces("known_faces")
    print(f"Stage 5: {name} registered as {role}. System updated.")

    # ✅ Say goodbye with reminder
    reminder_message = f"Thank you {name.capitalize()}. I will remind you to take your medication at {reminder_time}."
    speak_in_background(reminder_message)
