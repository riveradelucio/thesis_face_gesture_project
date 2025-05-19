import cv2
import time
import os

from app.face_recognition import detect_and_recognize, register_known_faces
from app.hi_wave_detector import detect_wave
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_gesture_animation
from app.conversation_manager import greet_user_by_role
from app.role_database import USER_ROLES, save_roles  # ✅ For saving new roles

def save_new_face_image(full_frame, name):
    filename = os.path.join("known_faces", f"{name.lower()}.jpg")
    cv2.imwrite(filename, full_frame)
    print(f"✅ Full frame saved as {filename}")

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Cannot access webcam.")
        return

    register_known_faces("known_faces")

    frame_count = 0
    faces = []
    interaction_started = False
    interaction_start_time = None

    show_wave_message_duration = 2
    gesture_start_delay = 2
    last_gesture = None
    gesture_last_time = 0
    gesture_display_duration = 2

    # New logic
    unrecognized_start_time = None
    recognition_timeout = 5  # seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # mirror effect
        frame_count += 1
        current_time = time.time()

        if frame_count % 3 == 0:
            faces = detect_and_recognize(frame, scale_factor=0.3)

        recognized = any(face["recognized"] for face in faces)

        # Step 1: Draw faces and start unrecognized timer if needed
        has_unrecognized_face = False
        for face in faces:
            x1, y1, x2, y2 = face["bbox"]
            label = face["name"]
            color = (0, 180, 0) if face["recognized"] else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if not face["recognized"]:
                has_unrecognized_face = True

        # Step 2: Track unrecognized time
        if has_unrecognized_face and not recognized:
            if unrecognized_start_time is None:
                unrecognized_start_time = current_time
            elif current_time - unrecognized_start_time > recognition_timeout:
                print("🆕 Unrecognized user for 5 seconds. Starting registration.")
                # Pause the loop
                cv2.imshow("Face + Gesture Recognition", frame)
                cv2.waitKey(1)

                # Prompt for user info
                name = input("Enter name for new user: ").strip().lower()
                role = input("Enter role (Elderly user / Family member / Caregiver): ").strip()

                # Save full frame (not just face)
                save_new_face_image(frame, name)

                # Update database
                USER_ROLES[name] = role
                save_roles(USER_ROLES)

                # Refresh face encoding
                register_known_faces("known_faces")

                print(f"✅ {name} registered as {role}. System updated.")

                # Reset unrecognized timer
                unrecognized_start_time = None
                continue  # skip rest of loop this frame
        else:
            unrecognized_start_time = None  # Reset timer if face becomes recognized

        # Step 3: Start interaction on wave
        if recognized and not interaction_started:
            if detect_wave(frame):
                print("👋 Wave Detected! Starting interaction.")
                interaction_started = True
                interaction_start_time = current_time

                for face in faces:
                    if face["recognized"]:
                        greet_user_by_role(face["name"])
                        break

        # Step 4: Show wave message
        if interaction_start_time and current_time - interaction_start_time < show_wave_message_duration:
            cv2.putText(frame, "Hi detected!", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 100, 0), 3)

        # Step 5: Gesture detection
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

        # Step 6: Show camera window
        cv2.imshow("Face + Gesture Recognition", frame)

        # Step 7: Quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
