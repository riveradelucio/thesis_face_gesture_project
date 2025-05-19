import os
import cv2
import threading

from app.role_database import USER_ROLES, save_roles
from app.face_recognition import register_known_faces
from app.text_to_speech import speak_text

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
    thread.start()

def save_new_face_image(full_frame, name):
    print("👉 Stage 3: Preparing to save image...")
    filename = os.path.join("known_faces", f"{name.lower()}.jpg")

    # 🧪 Comment this line to test if it causes freeze:
    cv2.imwrite(filename, full_frame)

    print(f"✅ Stage 3: Image saved as {filename}")

def handle_new_user_registration(frame):
    print("🔄 Stage 1: Starting user registration")

    speak_in_background("I can't recognize you. Could you stay still and type your name?")

    print("⌨️ Stage 2: Waiting for user input...")
    name = input("Enter name for new user: ").strip().lower()
    role = input("Enter role (Elderly user / Family member / Caregiver): ").strip()
    print(f"📝 Name: {name}, Role: {role}")

    save_new_face_image(frame, name)

    print("📂 Stage 4: Saving role and updating face database...")
    USER_ROLES[name] = role
    save_roles(USER_ROLES)
    register_known_faces("known_faces")
    print(f"✅ Stage 5: {name} registered as {role}. System updated.")
