import threading
from app.new_user_registration import handle_new_user_registration
from app.conversation_manager import greet_user_by_role
from app.gesture_responder import overlay_centered_animation
from app.config import (
    FONT, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_THICKNESS,
    COLOR_YELLOW, COLOR_GRAY, COLOR_PINK,
    IDLE_ANIMATION_NAME, GESTURE_DISPLAY_DURATION,
    GESTURE_START_DELAY, SHOW_WAVE_MESSAGE_DURATION
)
import cv2


def check_for_registration_trigger(has_unrecognized_face, recognized, state, current_time, unrecognized_start_time, recognition_timeout):
    """
    Check if we should start waiting for a wave from an unknown face.
    Returns the updated unrecognized_start_time.
    """
    if has_unrecognized_face and not recognized and not state.registration_in_progress:
        if unrecognized_start_time is None:
            return current_time
        elif current_time - unrecognized_start_time > recognition_timeout:
            state.awaiting_wave = True
    else:
        state.awaiting_wave = False
        return None
    return unrecognized_start_time


def check_wave_and_start_registration(frame, state):
    """
    If someone is waving and we're waiting, start the registration process.
    """
    from app.hi_wave_detector import detect_wave

    if state.awaiting_wave and detect_wave(frame):
        print("👋 Wave detected from unrecognized user. Starting registration.")
        state.show_typing_prompt = True
        state.registration_in_progress = True
        state.awaiting_wave = False
        threading.Thread(
            target=run_registration_flow,
            args=(frame.copy(), state)
        ).start()


def run_registration_flow(frame, state):
    """
    This runs in the background when a new user is registering.
    """
    import os
    import sys
    import time

    handle_new_user_registration(frame)

    print("🔄 Requesting system restart...")
    time.sleep(1)

    state.request_restart = True

    # ✅ Fallback in case main loop doesn’t restart
    time.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)








def start_interaction_if_wave(frame, faces, interaction_started, current_time):
    """
    If a known face waves, start the interaction (greeting).
    """
    from app.hi_wave_detector import detect_wave

    if detect_wave(frame):
        print("👋 Wave Detected! Starting interaction.")
        interaction_started = True
        for face in faces:
            if face["recognized"]:
                greet_user_by_role(face["name"])
                break
        return interaction_started, current_time
    return interaction_started, None


def draw_interaction_status(black_frame, current_time, interaction_start_time, last_gesture, gesture_last_time, state):
    """
    Draws messages like 'Hi detected!' or 'Interaction Running...',
    and shows the idle animation if needed.
    """
    if interaction_start_time:
        time_since_start = current_time - interaction_start_time
        if time_since_start < SHOW_WAVE_MESSAGE_DURATION:
            cv2.putText(black_frame, "Hi detected!", (20, 50),
                        FONT, FONT_SIZE_LARGE, COLOR_YELLOW, FONT_THICKNESS)

            black_frame = overlay_centered_animation(
                black_frame,
                "Speaking",
                interaction_start_time,
                duration=SHOW_WAVE_MESSAGE_DURATION
            )

        elif time_since_start >= GESTURE_START_DELAY:
            if not last_gesture or current_time - gesture_last_time >= GESTURE_DISPLAY_DURATION:
                black_frame = overlay_centered_animation(
                    black_frame,
                    IDLE_ANIMATION_NAME,
                    state.idle_start_time
                )
            cv2.putText(black_frame, "Interaction Running...", (20, 50),
                        FONT, FONT_SIZE_MEDIUM, COLOR_GRAY, FONT_THICKNESS)

    # 👉 Show animation if user is in registration typing phase
    if state.show_typing_prompt:
        black_frame = overlay_centered_animation(
            black_frame,
            "Cant_recognize_you",
            state.idle_start_time,
            duration=3.0
        )
        cv2.putText(black_frame, "Please type your name and role on the keyboard...", (20, 50),
                    FONT, FONT_SIZE_MEDIUM, COLOR_PINK, FONT_THICKNESS)

    return black_frame
