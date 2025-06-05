import cv2
import time
import threading
import numpy as np
import textwrap

from app.face_recognition import detect_and_recognize, register_known_faces
from app.hi_wave_detector import detect_wave
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_centered_animation
from app.conversation_manager import greet_user_by_role
from app.new_user_registration import handle_new_user_registration
from app.role_database import USER_ROLES
from app.subtitle_manager import get_current_subtitle
from app.screen_camera_and_subtitles import add_user_preview, add_subtitles  # ✅ NEW
from app.config import (
    FONT,
    FONT_SIZE_MEDIUM, FONT_SIZE_LARGE,
    FONT_THICKNESS,
    COLOR_YELLOW, COLOR_GRAY, COLOR_PINK,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_NAME,
    IDLE_ANIMATION_NAME,
    GESTURE_DISPLAY_DURATION, GESTURE_START_DELAY,
    SHOW_WAVE_MESSAGE_DURATION, RECOGNITION_TIMEOUT
)

# ✅ App state grouped in a class
class AppState:
    def __init__(self):
        self.show_typing_prompt = False
        self.registration_in_progress = False
        self.awaiting_wave = False
        self.idle_start_time = time.time()

def main():
    state = AppState()

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

    last_gesture = None
    gesture_last_time = 0

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

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

        if has_unrecognized_face and not recognized and not state.registration_in_progress:
            if unrecognized_start_time is None:
                unrecognized_start_time = current_time
            elif current_time - unrecognized_start_time > RECOGNITION_TIMEOUT:
                state.awaiting_wave = True
        else:
            unrecognized_start_time = None
            state.awaiting_wave = False

        if state.awaiting_wave and detect_wave(frame):
            print("👋 Wave detected from unrecognized user. Starting registration.")
            state.show_typing_prompt = True
            state.registration_in_progress = True
            state.awaiting_wave = False
            threading.Thread(
                target=run_registration_flow,
                args=(frame.copy(), state)
            ).start()

        if recognized and not interaction_started:
            if detect_wave(frame):
                print("👋 Wave Detected! Starting interaction.")
                interaction_started = True
                interaction_start_time = current_time
                for face in faces:
                    if face["recognized"]:
                        greet_user_by_role(face["name"])
                        break

        black_frame = np.zeros((frame.shape[0], int(frame.shape[1] * 0.8), 3), dtype=np.uint8)

        if not interaction_started and not state.registration_in_progress and (
            not last_gesture or current_time - gesture_last_time >= GESTURE_DISPLAY_DURATION):
            black_frame = overlay_centered_animation(black_frame, IDLE_ANIMATION_NAME, state.idle_start_time)

        if interaction_start_time:
            if current_time - interaction_start_time < SHOW_WAVE_MESSAGE_DURATION:
                cv2.putText(black_frame, "Hi detected!", (20, 50),
                            FONT, FONT_SIZE_LARGE, COLOR_YELLOW, FONT_THICKNESS)
                black_frame = overlay_centered_animation(
                    black_frame, "Speaking", interaction_start_time, duration=SHOW_WAVE_MESSAGE_DURATION)
            elif current_time - interaction_start_time >= GESTURE_START_DELAY:
                if not last_gesture or current_time - gesture_last_time >= GESTURE_DISPLAY_DURATION:
                    black_frame = overlay_centered_animation(black_frame, IDLE_ANIMATION_NAME, state.idle_start_time)
                cv2.putText(black_frame, "Interaction Running...", (20, 50),
                            FONT, FONT_SIZE_MEDIUM, COLOR_GRAY, FONT_THICKNESS)

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

        if state.show_typing_prompt:
            cv2.putText(black_frame, "Please type your name and role on the keyboard...", (20, 460),
                        FONT, FONT_SIZE_MEDIUM, COLOR_PINK, FONT_THICKNESS)

        # ✅ Use helper to add camera preview
        final_display = add_user_preview(black_frame.copy(), full_frame)

        # ✅ Use helper to add subtitles
        subtitle_text = get_current_subtitle()
        final_display = add_subtitles(final_display, subtitle_text)

        cv2.imshow(WINDOW_NAME, final_display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def run_registration_flow(frame, state):
    handle_new_user_registration(frame)
    state.show_typing_prompt = False
    state.registration_in_progress = False

if __name__ == "__main__":
    main()
