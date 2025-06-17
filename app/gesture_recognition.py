import cv2
import mediapipe as mp
import math
from collections import deque

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh()

# Constants
finger_tips = [4, 8, 12, 16, 20]
MOUTH_TOP = 13
LEFT_EYE_POINTS = [33, 145, 159]
RIGHT_EYE_POINTS = [263, 374, 386]
LEFT_EAR_POINTS = [234, 93]
RIGHT_EAR_POINTS = [454, 323]

# State memory for "Stop"
hand_position_buffers = [deque(maxlen=5), deque(maxlen=5)]
stop_still_counters = [0, 0]
STOP_THRESHOLD_FRAMES = 8
STOP_MOVEMENT_THRESHOLD = 10  # Pixels

def detect_custom_gesture(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result_hands = hands.process(rgb)
    result_face = face.process(rgb)

    all_hands = []
    mouth_pos = None
    left_eye_positions = []
    right_eye_positions = []
    left_ear_positions = []
    right_ear_positions = []

    if result_face.multi_face_landmarks:
        for faceLms in result_face.multi_face_landmarks:
            h, w, _ = frame.shape
            for i, lm in enumerate(faceLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                if i == MOUTH_TOP:
                    mouth_pos = (cx, cy)
                if i in LEFT_EYE_POINTS:
                    left_eye_positions.append((cx, cy))
                if i in RIGHT_EYE_POINTS:
                    right_eye_positions.append((cx, cy))
                if i in LEFT_EAR_POINTS:
                    left_ear_positions.append((cx, cy))
                if i in RIGHT_EAR_POINTS:
                    right_ear_positions.append((cx, cy))

    if result_hands.multi_hand_landmarks and result_hands.multi_handedness:
        for idx, (handLms, handInfo) in enumerate(zip(result_hands.multi_hand_landmarks, result_hands.multi_handedness)):
            if idx > 1:
                continue
            handedness = handInfo.classification[0].label
            lm_list = []
            h, w, _ = frame.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))
            all_hands.append(lm_list)

            wrist = next((x for x in lm_list if x[0] == 0), None)
            middle_tip = next((x for x in lm_list if x[0] == 12), None)
            hand_center = middle_tip if middle_tip else wrist

            if hand_center:
                hand_position_buffers[idx].append((hand_center[1], hand_center[2]))

            moving = False
            if len(hand_position_buffers[idx]) == hand_position_buffers[idx].maxlen:
                xs = [x for x, y in hand_position_buffers[idx]]
                ys = [y for x, y in hand_position_buffers[idx]]
                dx = max(xs) - min(xs)
                dy = max(ys) - min(ys)
                if dx > STOP_MOVEMENT_THRESHOLD or dy > STOP_MOVEMENT_THRESHOLD:
                    moving = True

            fingers = []
            if handedness == 'Right':
                fingers.append(1 if lm_list[4][1] < lm_list[3][1] else 0)
            else:
                fingers.append(1 if lm_list[4][1] > lm_list[3][1] else 0)
            for tip_id in finger_tips[1:]:
                fingers.append(1 if lm_list[tip_id][2] < lm_list[tip_id - 2][2] else 0)

            if sum(fingers) == 5:
                if not moving:
                    stop_still_counters[idx] += 1
                    if stop_still_counters[idx] >= STOP_THRESHOLD_FRAMES:
                        return "Stop"
                else:
                    stop_still_counters[idx] = 0
            else:
                stop_still_counters[idx] = 0

    if len(all_hands) == 1:
        return _detect_one_hand(all_hands[0], mouth_pos, left_ear_positions, right_ear_positions)
    if len(all_hands) == 2:
        return _detect_two_hands(all_hands[0], all_hands[1], left_eye_positions, right_eye_positions)

    return None

def is_thumb_only(lm_list, relaxed=False):
    thumb_up = lm_list[4][2] < lm_list[3][2]
    folded_scores = [lm_list[tip][2] > lm_list[tip - 2][2] for tip in finger_tips[1:]]

    if relaxed:
        folded_fingers = sum(folded_scores) >= 3
    else:
        folded_fingers = all(folded_scores)

    return thumb_up and folded_fingers

def is_thumb_down(lm_list):
    thumb_down = lm_list[4][2] > lm_list[3][2]
    folded_scores = [lm_list[tip][2] > lm_list[tip - 2][2] for tip in finger_tips[1:]]
    folded_fingers = sum(folded_scores) >= 2  # More tolerant

    return thumb_down and folded_fingers

def _detect_one_hand(lm_list, mouth_pos, left_ear, right_ear):
    wrist = next((x for x in lm_list if x[0] == 0), None)
    thumb_tip = next((x for x in lm_list if x[0] == 4), None)
    thumb_ip = next((x for x in lm_list if x[0] == 3), None)

    if wrist and thumb_tip and thumb_ip:
        if is_thumb_only(lm_list):
            if thumb_tip[2] < wrist[2] - 10:
                return "Thumbs_Up"
        if is_thumb_down(lm_list):
            if thumb_tip[2] > wrist[2] + 10:
                return "Thumbs_Down"

    index_finger = next((x for x in lm_list if x[0] == 8), None)
    middle_tip = next((x for x in lm_list if x[0] == 12), None)

    if mouth_pos and index_finger and middle_tip:
        fingers_distance = math.hypot(index_finger[1] - middle_tip[1], index_finger[2] - middle_tip[2])
        avg_x = (index_finger[1] + middle_tip[1]) / 2
        avg_y = (index_finger[2] + middle_tip[2]) / 2
        dist_to_mouth = math.hypot(avg_x - mouth_pos[0], avg_y - mouth_pos[1])
        if fingers_distance < 40 and avg_y > mouth_pos[1] and dist_to_mouth < 100:
            return "Eat"

    if index_finger and mouth_pos:
        dist_to_mouth = math.hypot(index_finger[1] - mouth_pos[0], index_finger[2] - mouth_pos[1])
        if dist_to_mouth < 40:
            return "Silence"

    if index_finger:
        for ex, ey in left_ear + right_ear:
            dist = math.hypot(index_finger[1] - ex, index_finger[2] - ey)
            if dist < 40:
                return "Cant_hear"

    return None

def _detect_two_hands(hand1, hand2, left_eye_pos, right_eye_pos):
    tips1 = [x for x in hand1 if x[0] in [8, 12, 16]]
    tips2 = [x for x in hand2 if x[0] in [8, 12, 16]]

    if left_eye_pos and right_eye_pos:
        left_detected = any(
            math.hypot(t1[1] - ex, t1[2] - ey) < 80
            for t1 in tips1 for (ex, ey) in left_eye_pos
        )
        right_detected = any(
            math.hypot(t2[1] - ex, t2[2] - ey) < 80
            for t2 in tips2 for (ex, ey) in right_eye_pos
        )
        if left_detected and right_detected:
            return "Cover_eyes"

    thumb1 = next((x for x in hand1 if x[0] == 4), None)
    thumb2 = next((x for x in hand2 if x[0] == 4), None)
    pinky1 = next((x for x in hand1 if x[0] == 20), None)
    pinky2 = next((x for x in hand2 if x[0] == 20), None)
    if thumb1 and thumb2 and pinky1 and pinky2:
        thumb_dist = math.hypot(thumb1[1] - thumb2[1], thumb1[2] - thumb2[2])
        pinky_dist = math.hypot(pinky1[1] - pinky2[1], pinky1[2] - pinky2[2])
        if thumb_dist < 60 and pinky_dist < 60:
            return "Heart"

    return None
