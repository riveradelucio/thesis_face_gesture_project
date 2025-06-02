import cv2
import time
import os
import threading
import numpy as np
import textwrap

from app.face_recognition import detect_and_recognize, register_known_faces
from app.hi_wave_detector import detect_wave
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_gesture_animation
from app.conversation_manager import greet_user_by_role
from app.new_user_registration import handle_new_user_registration
from app.role_database import USER_ROLES
from app.subtitle_manager import get_current_subtitle

# Global flags
show_typing_prompt = False
registration_in_progress = False
awaiting_wave = False

# Idle animation config (💤 Blinking avatar before interaction)
idle_animation_name = "Idle_state"  # Folder name in reactions
idle_start_time = time.time()


def main():
    global show_typing_prompt, registration_in_progress, awaiting_wave, idle_start_time

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

    window_width = 700
    window_height = 500
    window_name = "Face + Gesture Recognition"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, window_width, window_height)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame_count += 1
        current_time = time.time()

        full_frame = frame.copy()

        if frame_count % 3 == 0:
            faces = detect_and_recognize(frame, scale_factor=0.3)

        recognized = any(face["recognized"] for face in faces)
        has_unrecognized_face = any(not face["recognized"] for face in faces)

        # Step 1: Trigger registration if unrecognized + wave
        if has_unrecognized_face and not recognized and not registration_in_progress:
            if unrecognized_start_time is None:
                unrecognized_start_time = current_time
            elif current_time - unrecognized_start_time > recognition_timeout:
                awaiting_wave = True
        else:
            unrecognized_start_time = None
            awaiting_wave = False

        # Step 2: Detect wave to confirm intent to register
        if awaiting_wave and detect_wave(frame):
            print("👋 Wave detected from unrecognized user. Starting registration.")
            show_typing_prompt = True
            registration_in_progress = True
            awaiting_wave = False
            threading.Thread(
                target=run_registration_flow,
                args=(frame.copy(),)
            ).start()

        # Step 3: Detect wave from known user to start interaction
        if recognized and not interaction_started:
            if detect_wave(frame):
                print("👋 Wave Detected! Starting interaction.")
                interaction_started = True
                interaction_start_time = current_time
                for face in faces:
                    if face["recognized"]:
                        greet_user_by_role(face["name"])
                        break

        # Step 4: Create black canvas for center
        black_frame = np.zeros((frame.shape[0], int(frame.shape[1] * 0.8), 3), dtype=np.uint8)

        # Step 5: Show idle blinking animation if waiting
        if not interaction_started and not registration_in_progress:
            black_frame = overlay_gesture_animation(
                black_frame,
                gesture_name=idle_animation_name,
                start_time=idle_start_time,
                duration=2.5,
                scale=0.3,
                x=80,
                y=black_frame.shape[0] // 2 - 100
            )

        # Step 6: Show interaction messages
        if interaction_start_time:
            if current_time - interaction_start_time < show_wave_message_duration:
                cv2.putText(black_frame, "Hi detected!", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            elif current_time - interaction_start_time >= gesture_start_delay:
                cv2.putText(black_frame, "Interaction Running...", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)

        # Step 7: Gesture detection
        if interaction_started and current_time - interaction_start_time >= gesture_start_delay:
            gesture = detect_custom_gesture(frame)
            if gesture and (gesture != last_gesture or current_time - gesture_last_time > gesture_display_duration):
                print(f"🖐️ Detected gesture: {gesture}")
                last_gesture = gesture
                gesture_last_time = current_time

            if last_gesture and current_time - gesture_last_time < gesture_display_duration:
                black_frame = overlay_gesture_animation(
                    black_frame,
                    last_gesture,
                    gesture_last_time,
                    duration=gesture_display_duration,
                    x=black_frame.shape[1] // 2 - 100,
                    y=black_frame.shape[0] // 2 - 100,
                    scale=0.3
                )

        # Step 8: Typing prompt
        if show_typing_prompt:
            cv2.putText(black_frame, "Please type your name and role on the keyboard...", (20, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (280, 180, 180), 2)

        # Step 9: Show bottom-right user webcam view
        user_view_small = cv2.resize(
            full_frame,
            (int(frame.shape[1] * 0.2), int(frame.shape[0] * 0.3)),
            interpolation=cv2.INTER_AREA
        )
        final_display = black_frame.copy()
        y_offset = final_display.shape[0] - user_view_small.shape[0] - 10
        x_offset = final_display.shape[1] - user_view_small.shape[1] - 10
        final_display[y_offset:y_offset + user_view_small.shape[0],
                      x_offset:x_offset + user_view_small.shape[1]] = user_view_small

        # Step 10: Subtitles
        subtitle_text = get_current_subtitle()
        if subtitle_text:
            max_line_width = 45
            wrapped_lines = textwrap.wrap(subtitle_text, width=max_line_width)
            line_height = 25
            subtitle_y = final_display.shape[0] - line_height * len(wrapped_lines) - 10
            for i, line in enumerate(wrapped_lines):
                cv2.putText(final_display, line,
                            (20, subtitle_y + i * line_height),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        # Step 11: Final show
        cv2.imshow(window_name, final_display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_registration_flow(frame):
    global show_typing_prompt, registration_in_progress
    handle_new_user_registration(frame)
    show_typing_prompt = False
    registration_in_progress = False


if __name__ == "__main__":
    main()