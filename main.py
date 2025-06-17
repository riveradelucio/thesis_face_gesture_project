# main.py

import cv2
import time
import threading
import numpy as np
import os
import sys
import subprocess

from app.face_recognition import detect_and_recognize, register_known_faces
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_centered_animation
from app.role_database import USER_ROLES
from app.subtitle_manager import get_current_subtitle
from app.screen_camera_and_subtitles import add_user_preview, add_subtitles
from app.text_to_speech import speak_text
from app.hi_wave_detector import detect_wave

from app.interaction_flow import (
    check_for_registration_trigger,
    check_wave_and_start_registration,
    start_interaction_if_wave,
    draw_interaction_status,
    run_registration_flow,
    handle_goodbye_wave
)

from app.config import (
    FONT, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_THICKNESS,
    COLOR_PINK, COLOR_YELLOW,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_NAME,
    IDLE_ANIMATION_NAME,
    GESTURE_DISPLAY_DURATION, GESTURE_START_DELAY,
    SHOW_WAVE_MESSAGE_DURATION, RECOGNITION_TIMEOUT,
    RAW_BACKGROUND
)

def speak_in_background(message: str):
    thread = threading.Thread(target=speak_text, args=(message,))
    thread.start()

class AppState:
    def __init__(self):
        self.show_typing_prompt = False
        self.registration_in_progress = False
        self.awaiting_wave = False
        self.request_restart = False
        self.idle_start_time = time.time()

def main():
    while True:
        state = AppState()

        if state.request_restart:
            print("♻️ Restarting entire system now...")
            script_path = os.path.abspath(__file__)
            subprocess.Popen([sys.executable, script_path])
            sys.exit(0)

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

        wave_start_time = None
        REQUIRED_WAVE_DURATION = 1.8

        stable_gesture_buffer = []
        STABLE_GESTURE_FRAMES = 2
        MIN_TIME_BETWEEN_GESTURES = 2
        gesture_cooldown_until = 0

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

        user_requested_exit = False

        while True:
            if state.request_restart:
                break

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

            unrecognized_start_time = check_for_registration_trigger(
                has_unrecognized_face, recognized, state, current_time,
                unrecognized_start_time, RECOGNITION_TIMEOUT
            )

            check_wave_and_start_registration(frame, state)

            if recognized and not interaction_started:
                interaction_started, interaction_start_time = start_interaction_if_wave(
                    frame, faces, interaction_started, current_time
                )

            background_image = cv2.resize(RAW_BACKGROUND, (int(frame.shape[1] * 0.8), frame.shape[0]))
            black_frame = background_image.copy()

            if not interaction_started and not state.registration_in_progress and (
                not last_gesture or current_time - gesture_last_time >= GESTURE_DISPLAY_DURATION):
                black_frame = overlay_centered_animation(black_frame, IDLE_ANIMATION_NAME, state.idle_start_time)

            black_frame = draw_interaction_status(
                black_frame, current_time, interaction_start_time,
                last_gesture, gesture_last_time, state
            )

            if interaction_started and current_time - interaction_start_time >= GESTURE_START_DELAY:
                gesture = detect_custom_gesture(frame)

                if gesture:
                    if current_time >= gesture_cooldown_until:
                        stable_gesture_buffer.append(gesture)
                        if len(stable_gesture_buffer) > STABLE_GESTURE_FRAMES:
                            stable_gesture_buffer.pop(0)

                        if len(stable_gesture_buffer) == STABLE_GESTURE_FRAMES and all(g == gesture for g in stable_gesture_buffer):
                            print(f"🖐️ Detected stable gesture: {gesture}")
                            last_gesture = gesture
                            gesture_last_time = current_time
                            gesture_cooldown_until = current_time + MIN_TIME_BETWEEN_GESTURES
                    else:
                        stable_gesture_buffer.clear()
                else:
                    stable_gesture_buffer.clear()
                    if detect_wave(frame):
                        if wave_start_time is None:
                            wave_start_time = current_time
                        elif current_time - wave_start_time >= REQUIRED_WAVE_DURATION:
                            handle_goodbye_wave(frame, full_frame, cap)
                    else:
                        wave_start_time = None

                if last_gesture and current_time - gesture_last_time < GESTURE_DISPLAY_DURATION:
                    black_frame = overlay_centered_animation(
                        black_frame,
                        last_gesture,
                        gesture_last_time,
                        duration=GESTURE_DISPLAY_DURATION
                    )

                    cv2.putText(
                        black_frame,
                        f"{last_gesture.replace('_', ' ')} detected!",
                        (20, 50),
                        FONT,
                        FONT_SIZE_LARGE,
                        COLOR_YELLOW,
                        FONT_THICKNESS
                    )

            final_display = add_user_preview(black_frame.copy(), full_frame)
            subtitle_text = get_current_subtitle()
            final_display = add_subtitles(final_display, subtitle_text)

            cv2.imshow(WINDOW_NAME, final_display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                user_requested_exit = True
                break

        cap.release()
        cv2.destroyAllWindows()

        if user_requested_exit:
            break

if __name__ == "__main__":
    main()
