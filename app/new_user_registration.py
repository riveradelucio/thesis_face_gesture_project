import os
import time
import cv2

from app.role_database import USER_ROLES, save_roles
from app.face_recognition import register_known_faces
from app.text_to_speech import speak_text

def save_new_face_image(full_frame, name):
    """Save full image of the user to known_faces folder."""
    filename = os.path.join("known_faces", f"{name.lower()}.jpg")
    cv2.imwrite(filename, full_frame)
    print(f"✅ Full frame saved as {filename}")

def handle_new_user_registration(frame):
    """
    Handle the workflow to register a new user:
    1. Speak to the user
    2. Show message on camera
    3. Ask for name and role
    4. Save full frame
    5. Update roles and re-register faces
    """
    # Step 1: Speak message
    speak_text("I can't recognize you. Could you stay still?")

    # Step 2: Show message on screen before asking name
    display_frame = frame.copy()
    message = "Please type your name and role on the keyboard..."
    cv2.putText(display_frame, message, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Face + Gesture Recognition", display_frame)
    cv2.waitKey(1000)  # Wait 1 second while displaying message

    # Step 3: Ask for name and role (in terminal)
    name = input("Enter name for new user: ").strip().lower()
    role = input("Enter role (Elderly user / Family member / Caregiver): ").strip()

    # Step 4: Save image and update system
    save_new_face_image(frame, name)
    USER_ROLES[name] = role
    save_roles(USER_ROLES)
    register_known_faces("known_faces")

    print(f"✅ {name} registered as {role}. System updated.")
