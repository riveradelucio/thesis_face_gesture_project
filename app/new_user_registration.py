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
    """
    Speak a list of lines one after another in a background thread,
    showing subtitles for each.
    """
    def run():
        for line in lines:
            update_subtitle(line)
            speak_text(line)
            time.sleep(delay)

    thread = threading.Thread(target=run)
    thread.start()


def save_new_face_image(_, name):
    speak_in_background("Could you stay still for a moment? I will take a picture of you.")

    print("Stage 3: Waiting before taking picture...")
    time.sleep(5)  # Wait for the user to stay still

    print("Stage 3: Capturing new frame...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot access webcam to take picture.")
        return

    ret, fresh_frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to capture image.")
        return

    fresh_frame = cv2.flip(fresh_frame, 1)  # Flip to match live view
    filename = os.path.join("known_faces", f"{name.lower()}.jpg")
    cv2.imwrite(filename, fresh_frame)

    print(f"✅ Image saved as {filename}")


def handle_new_user_registration(frame):
    print("Stage 1: Starting user registration")

    # 🧠 Speak welcome and instructions in two separate messages
    speak_multiple_lines_in_background([
        "Hi there! I am Luis. I do not recognize you yet. Your face is new to me.",
        "Could you please type your name and role on the keyboard so we can get to know each other?"
    ])

    print("Stage 2: Waiting for user input...")
    name = input("Enter name for new user: ").strip().lower()

    # ✅ Step: Only allow fixed role options
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

    save_new_face_image(frame, name)

    print("Stage 4: Saving role and updating face database...")
    USER_ROLES[name] = role
    save_roles(USER_ROLES)
    register_known_faces("known_faces")
    print(f"Stage 5: {name} registered as {role}. System updated.")
