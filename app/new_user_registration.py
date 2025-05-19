import os
import cv2
import threading
import time

from app.role_database import USER_ROLES, save_roles
from app.face_recognition import register_known_faces
from app.text_to_speech import speak_text

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
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
    speak_in_background("I can't recognize you. Could type your name and role on the keyboard?")

    print("Stage 2: Waiting for user input...")
    name = input("Enter name for new user: ").strip().lower()
    role = input("Enter role (Elderly user / Family member / Caregiver): ").strip()
    print(f"Name: {name}, Role: {role}")

    save_new_face_image(frame, name)

    print("Stage 4: Saving role and updating face database...")
    USER_ROLES[name] = role
    save_roles(USER_ROLES)
    register_known_faces("known_faces")
    print(f"Stage 5: {name} registered as {role}. System updated.")
