import cv2
import mediapipe as mp
import math
from collections import deque

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)  # Allow both hands
mp_draw = mp.solutions.drawing_utils

# Track wrist x-positions for wave detection (for each hand)
wave_buffers = [deque(maxlen=5), deque(maxlen=5)]
still_counters = [0, 0]

cap = cv2.VideoCapture(0)

last_gesture = "No Hand Detected"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result_hands = hands.process(rgb)
    gesture = None

    if result_hands.multi_hand_landmarks and result_hands.multi_handedness:
        for idx, handLms in enumerate(result_hands.multi_hand_landmarks):
            if idx >= 2:
                break  # Only support 2 hands

            handedness = result_hands.multi_handedness[idx].classification[0].label  # 'Left' or 'Right'

            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            lm_list = []
            h, w, _ = frame.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            # Check if all 5 fingers are up
            finger_tips = [4, 8, 12, 16, 20]
            fingers = []

            # Since the camera sees the palm, we reverse thumb logic from before
            if handedness == 'Right':  # User's left hand
                if lm_list[4][1] < lm_list[3][1]:  # camera sees palm
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:  # Left hand (user's right hand)
                if lm_list[4][1] > lm_list[3][1]:  # camera sees palm
                    fingers.append(1)
                else:
                    fingers.append(0)

            for tip_id in finger_tips[1:]:
                if lm_list[tip_id][2] < lm_list[tip_id - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total_fingers = sum(fingers)

            # Track wrist movement for wave
            wrist = next((x for x in lm_list if x[0] == 0), None)
            middle_tip = next((x for x in lm_list if x[0] == 12), None)
            if wrist:
                wave_buffers[idx].append(wrist[1])  # x-coordinate

            waving_motion_detected = False
            if wrist and middle_tip and len(wave_buffers[idx]) == wave_buffers[idx].maxlen:
                hand_height = abs(wrist[2] - middle_tip[2]) + 1
                pixel_diff = max(wave_buffers[idx]) - min(wave_buffers[idx])
                scaled_diff = pixel_diff / hand_height
                if scaled_diff > 0.05:
                    waving_motion_detected = True

            if total_fingers == 5:
                if waving_motion_detected:
                    gesture = "Hi"
                    still_counters[idx] = 0
                else:
                    still_counters[idx] += 1
                    if still_counters[idx] >= 40:
                        gesture = "Stop"
            else:
                still_counters[idx] = 0

            if gesture:
                last_gesture = f"{gesture} ({handedness} Hand)"
    else:
        for i in range(2):
            wave_buffers[i].clear()
            still_counters[i] = 0
        last_gesture = ""

    # Show gesture
    cv2.putText(frame, last_gesture, (20, 60), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (0, 255, 0), 3)
    cv2.imshow("Hi & Stop Gesture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
