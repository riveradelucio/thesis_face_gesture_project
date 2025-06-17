# main_dumb.py

import cv2
import time
import numpy as np
from datetime import datetime
from dumb.dumb_user_registration import handle_dumb_user_registration
from app.config import RAW_BACKGROUND, WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from app.gesture_responder import overlay_centered_animation
from app.screen_camera_and_subtitles import add_subtitles
from app.subtitle_manager import update_subtitle

def detect_motion(frame, prev_frame, threshold=15):
    diff = cv2.absdiff(frame, prev_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) > threshold

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not available")
        return

    _, prev_frame = cap.read()
    prev_frame = cv2.flip(prev_frame, 1)

    last_trigger_time = 0
    cooldown = 10  # seconds to wait before reacting again
    last_known_user = None

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        background_frame = cv2.resize(RAW_BACKGROUND, (int(frame.shape[1] * 0.8), frame.shape[0]))

        motion_detected = detect_motion(frame, prev_frame)
        if motion_detected and (time.time() - last_trigger_time > cooldown):
            print("👀 Motion detected")
            last_known_user = handle_dumb_user_registration(
                cap, WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, last_known_user
            )
            last_trigger_time = time.time()

        prev_frame = frame.copy()

        idle_frame = overlay_centered_animation(background_frame.copy(), "Idle_state", time.time())
        idle_frame = add_subtitles(idle_frame, update_subtitle("") or "")

        cv2.imshow(WINDOW_NAME, idle_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
