import cv2
import time
import threading
import numpy as np

from app.face_recognition import detect_and_recognize, register_known_faces
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_centered_animation
from app.role_database import USER_ROLES
from app.subtitle_manager import get_current_subtitle
from app.screen_camera_and_subtitles import add_user_preview, add_subtitles
from app.interaction_flow import (
    check_for_registration_trigger,
    check_wave_and_start_registration,
    start_interaction_if_wave,
    draw_interaction_status,
    run_registration_flow
)
from app.config import (
    FONT, FONT_SIZE_MEDIUM, FONT_THICKNESS,
    COLOR_PINK,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_NAME,
    IDLE_ANIMATION_NAME,
    GESTURE_DISPLAY_DURATION, GESTURE_START_DELAY,
    SHOW_WAVE_MESSAGE_DURATION, RECOGNITION_TIMEOUT
)

# ✅ Holds all dynamic app variables (so we avoid global variables)
class AppState:
    def __init__(self):
        self.show_typing_prompt = False
        self.registration_in_progress = False
        self.awaiting_wave = False
        self.idle_start_time = time.time()

def main():
    state = AppState()

    # Step 1: Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot access webcam.")
        return

    # Step 2: Load known faces
    register_known_faces("known_faces")

    frame_count = 0
    faces = []
    interaction_started = False
    interaction_start_time = None
    unrecognized_start_time = None

    last_gesture = None
    gesture_last_time = 0

    # Step 3: Setup display window
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

    while True:
        # Step 4: Capture and mirror frame
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_count += 1
        current_time = time.time()
        full_frame = frame.copy()

        # Step 5: Run face recognition every few frames
        if frame_count % 3 == 0:
            faces = detect_and_recognize(frame, scale_factor=0.3)

        recognized = any(face["recognized"] for face in faces)
        has_unrecognized_face = any(not face["recognized"] for face in faces)

        # Step 6: Check if new face should register
        unrecognized_start_time = check_for_registration_trigger(
            has_unrecognized_face, recognized, state, current_time,
            unrecognized_start_time, RECOGNITION_TIMEOUT
        )

        # Step 7: Check if new user waves to register
        check_wave_and_start_registration(frame, state)

        # Step 8: Check if known user waves to begin interaction
        if recognized and not interaction_started:
            interaction_started, interaction_start_time = start_interaction_if_wave(
                frame, faces, interaction_started, current_time
            )

        # Step 9: Prepare background canvas
        black_frame = np.zeros((frame.shape[0], int(frame.shape[1] * 0.8), 3), dtype=np.uint8)

        # Step 10: Show idle animation if nothing is happening
        if not interaction_started and not state.registration_in_progress and (
            not last_gesture or current_time - gesture_last_time >= GESTURE_DISPLAY_DURATION):
            black_frame = overlay_centered_animation(black_frame, IDLE_ANIMATION_NAME, state.idle_start_time)

        # Step 11: Show messages like "Hi detected!"
        black_frame = draw_interaction_status(
            black_frame, current_time, interaction_start_time,
            last_gesture, gesture_last_time, state
        )

        # Step 12: Handle gesture recognition and display
        if interaction_started and current_time - interaction_start_time >= GESTURE_START_DELAY:
            gesture = detect_custom_gesture(frame)
            if gesture and (gesture != last_gesture or current_time - gesture_last_time > GESTURE_DISPLAY_DURATION):
                print(f"🖐️ Detected gesture: {gesture}")
                last_gesture = gesture
                gesture_last_time = current_time

            if last_gesture and current_time - gesture_last_time < GESTURE_DISPLAY_DURATION:
                black_frame = overlay_centered_animation(
                    black_frame,
                    last_gesture,
                    gesture_last_time,
                    duration=GESTURE_DISPLAY_DURATION
                )

        # Step 13: Show text if waiting for user to type name and role
        if state.show_typing_prompt:
            cv2.putText(black_frame, "Please type your name and role on the keyboard...", (20, 460),
                        FONT, FONT_SIZE_MEDIUM, COLOR_PINK, FONT_THICKNESS)

        # Step 14: Add small camera preview and subtitles
        final_display = add_user_preview(black_frame.copy(), full_frame)
        subtitle_text = get_current_subtitle()
        final_display = add_subtitles(final_display, subtitle_text)

        # Step 15: Display everything on screen
        cv2.imshow(WINDOW_NAME, final_display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Step 16: Cleanup camera and window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
