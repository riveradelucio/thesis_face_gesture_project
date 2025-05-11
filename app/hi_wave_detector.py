import cv2
import mediapipe as mp
import math
from collections import deque

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
wave_buffers = [deque(maxlen=5), deque(maxlen=5)]
still_counters = [0, 0]

def detect_wave(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for idx, handLms in enumerate(result.multi_hand_landmarks):
            if idx >= 2:
                continue

            handedness = result.multi_handedness[idx].classification[0].label
            lm_list = []
            h, w, _ = frame.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            # 5 fingers up?
            finger_tips = [4, 8, 12, 16, 20]
            fingers = []

            if handedness == 'Right':
                fingers.append(1 if lm_list[4][1] < lm_list[3][1] else 0)
            else:
                fingers.append(1 if lm_list[4][1] > lm_list[3][1] else 0)

            for tip_id in finger_tips[1:]:
                fingers.append(1 if lm_list[tip_id][2] < lm_list[tip_id - 2][2] else 0)

            total_fingers = sum(fingers)

            wrist = next((x for x in lm_list if x[0] == 0), None)
            middle_tip = next((x for x in lm_list if x[0] == 12), None)
            if wrist:
                wave_buffers[idx].append(wrist[1])

            waving = False
            if wrist and middle_tip and len(wave_buffers[idx]) == wave_buffers[idx].maxlen:
                hand_height = abs(wrist[2] - middle_tip[2]) + 1
                pixel_diff = max(wave_buffers[idx]) - min(wave_buffers[idx])
                scaled_diff = pixel_diff / hand_height
                if scaled_diff > 0.05:
                    waving = True

            if total_fingers == 5:
                if waving:
                    return True  # Hi detected

    return False  # No Hi
