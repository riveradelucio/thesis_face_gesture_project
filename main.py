import cv2
import time
import os
import threading

from app.face_recognition import detect_and_recognize, register_known_faces
from app.hi_wave_detector import detect_wave
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_gesture_animation
from app.conversation_manager import greet_user_by_role
from app.new_user_registration import handle_new_user_registration
from app.role_database import USER_ROLES

# ✅ Global flags
show_typing_prompt = False
registration_in_progress = False
awaiting_wave = False

def main():
    global show_typing_prompt, registration_in_progress, awaiting_wave

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot access webcam.")
        return

    register_known_faces("known_faces")

    frame_count = 0
    faces = []
    interaction_started = False
    interaction_start_time = None
    unrecognized_start_time = None
    recognition_timeout = 5  # seconds

    show_wave_message_duration = 2
    gesture_start_delay = 2
    last_gesture = None
    gesture_last_time = 0
    gesture_display_duration = 2

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame_count += 1
        current_time = time.time()

        if frame_count % 3 == 0:
            faces = detect_and_recognize(frame, scale_factor=0.3)

        recognized = any(face["recognized"] for face in faces)
        has_unrecognized_face = any(not face["recognized"] for face in faces)

        # Step 1: Draw face labels
        for face in faces:
            x1, y1, x2, y2 = face["bbox"]
            label = face["name"]
            color = (0, 180, 0) if face["recognized"] else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Step 2: Trigger registration if unrecognized + wave
        if has_unrecognized_face and not recognized and not registration_in_progress:
            if unrecognized_start_time is None:
                unrecognized_start_time = current_time
            elif current_time - unrecognized_start_time > recognition_timeout:                
                awaiting_wave = True
        else:
            unrecognized_start_time = None
            awaiting_wave = False

        # Step 3: Detect wave to confirm intent to register
        if awaiting_wave and detect_wave(frame):
            print("👋 Wave detected from unrecognized user. Starting registration.")
            show_typing_prompt = True
            registration_in_progress = True
            awaiting_wave = False
            threading.Thread(
                target=run_registration_flow,
                args=(frame.copy(),)
            ).start()

        # Step 4: Detect wave from known user to start interaction
        if recognized and not interaction_started:
            if detect_wave(frame):
                print("👋 Wave Detected! Starting interaction.")
                interaction_started = True
                interaction_start_time = current_time
                for face in faces:
                    if face["recognized"]:
                        greet_user_by_role(face["name"])
                        break

        # Step 5: Show greeting text
        if interaction_start_time and current_time - interaction_start_time < show_wave_message_duration:
            cv2.putText(frame, "Hi detected!", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 100, 0), 3)

        # Step 6: Gesture recognition
        if interaction_started and current_time - interaction_start_time >= gesture_start_delay:
            cv2.putText(frame, "Interaction Running...", (20, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (280, 180, 180), 2)

            gesture = detect_custom_gesture(frame)
            if gesture and (gesture != last_gesture or current_time - gesture_last_time > gesture_display_duration):
                print(f"🖐️ Detected gesture: {gesture}")
                last_gesture = gesture
                gesture_last_time = current_time

            if last_gesture and current_time - gesture_last_time < gesture_display_duration:
                frame = overlay_gesture_animation(
                    frame,
                    last_gesture,
                    gesture_last_time,
                    duration=gesture_display_duration,
                    x=600,
                    y=600,
                    scale=0.2
                )

        # Step 7: Show typing prompt during registration
        if show_typing_prompt:
            cv2.putText(frame, "Please type your name and role on the keyboard...", (20, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (280, 180, 180), 2)

        # Step 8: Show camera
        cv2.imshow("Face + Gesture Recognition", frame)

        # Step 9: Exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Step 10: Registration callback
def run_registration_flow(frame):
    global show_typing_prompt, registration_in_progress
    handle_new_user_registration(frame)
    show_typing_prompt = False
    registration_in_progress = False

if __name__ == "__main__":
    main()
