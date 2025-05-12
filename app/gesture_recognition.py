import cv2
import mediapipe as mp
import math

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh()
finger_tips = [4, 8, 12, 16, 20]

# Face landmark IDs
MOUTH_TOP = 13
LEFT_EYE_POINTS = [33, 145, 159]
RIGHT_EYE_POINTS = [263, 374, 386]
LEFT_EAR_POINTS = [234, 93]
RIGHT_EAR_POINTS = [454, 323]

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

    # Face landmarks
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

    # Hand landmarks
    if result_hands.multi_hand_landmarks:
        for handLms in result_hands.multi_hand_landmarks:
            lm_list = []
            h, w, _ = frame.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))
            all_hands.append(lm_list)

    if all_hands:
        if len(all_hands) == 1:
            return _detect_one_hand(all_hands[0], mouth_pos, left_ear_positions, right_ear_positions)
        elif len(all_hands) == 2:
            return _detect_two_hands(all_hands[0], all_hands[1], left_eye_positions, right_eye_positions)
    return None

def _detect_one_hand(lm_list, mouth_pos, left_ear, right_ear):
    # Detect fingers
    fingers = [1 if lm_list[4][2] < lm_list[3][2] else 0]  # Thumb up
    for tip_id in finger_tips[1:]:
        fingers.append(1 if lm_list[tip_id][2] < lm_list[tip_id - 2][2] else 0)
    total_fingers = sum(fingers)

    # 👍 Thumbs Up: thumb up, others folded
    if lm_list[4][2] < lm_list[3][2] and all(lm_list[tip_id][2] > lm_list[tip_id - 2][2] for tip_id in finger_tips[1:]):
        return "Thumbs_Up"

    # 👎 Thumbs Down: thumb down, others folded
    if lm_list[4][2] > lm_list[3][2] and all(lm_list[tip_id][2] > lm_list[tip_id - 2][2] for tip_id in finger_tips[1:]):
        return "Thumbs_Down"

    if total_fingers == 0:
        return "Fist"
    elif total_fingers == 2 and fingers[1] == 1 and fingers[2] == 1:
        return "Peace"
    elif total_fingers == 5:
        return "Stop"

    index_finger = next((x for x in lm_list if x[0] == 8), None)
    middle_tip = next((x for x in lm_list if x[0] == 12), None)

    # 🍽 Eat
    if mouth_pos and index_finger and middle_tip:
        fingers_distance = math.hypot(index_finger[1] - middle_tip[1], index_finger[2] - middle_tip[2])
        avg_x = (index_finger[1] + middle_tip[1]) / 2
        avg_y = (index_finger[2] + middle_tip[2]) / 2
        dist_to_mouth = math.hypot(avg_x - mouth_pos[0], avg_y - mouth_pos[1])
        if fingers_distance < 40 and avg_y > mouth_pos[1] and dist_to_mouth < 100:
            return "Eat"

    # 🤫 Silence
    if index_finger and mouth_pos:
        dist_to_mouth = math.hypot(index_finger[1] - mouth_pos[0], index_finger[2] - mouth_pos[1])
        if dist_to_mouth < 40:
            return "Silence"

    # 🧏 Can't hear
    if index_finger:
        for ex, ey in left_ear + right_ear:
            dist = math.hypot(index_finger[1] - ex, index_finger[2] - ey)
            if dist < 40:
                return "Cant_hear"

    return None

def _detect_two_hands(hand1, hand2, left_eye_pos, right_eye_pos):
    # 🙈 Cover Eyes
    tips1 = [x for x in hand1 if x[0] in [8, 12, 16]]
    tips2 = [x for x in hand2 if x[0] in [8, 12, 16]]
    if left_eye_pos and right_eye_pos:
        for tip1 in tips1:
            for (ex, ey) in left_eye_pos:
                if math.hypot(tip1[1] - ex, tip1[2] - ey) < 60:
                    for tip2 in tips2:
                        for (ex2, ey2) in right_eye_pos:
                            if math.hypot(tip2[1] - ex2, tip2[2] - ey2) < 60:
                                return "Cover_eyes"

    # ❤️ Heart
    thumb1 = next((x for x in hand1 if x[0] == 4), None)
    thumb2 = next((x for x in hand2 if x[0] == 4), None)
    pinky1 = next((x for x in hand1 if x[0] == 20), None)
    pinky2 = next((x for x in hand2 if x[0] == 20), None)
    if thumb1 and thumb2 and pinky1 and pinky2:
        thumb_dist = math.hypot(thumb1[1] - thumb2[1], thumb1[2] - thumb2[2])
        pinky_dist = math.hypot(pinky1[1] - pinky2[1], pinky1[2] - pinky2[2])
        if thumb_dist < 60 and pinky_dist < 60:
            return "Heart"

    # 👏 Clap
    finger_ids = [8, 12, 16]
    fingers1 = [x for x in hand1 if x[0] in finger_ids]
    fingers2 = [x for x in hand2 if x[0] in finger_ids]
    close = 0
    for f1 in fingers1:
        for f2 in fingers2:
            if math.hypot(f1[1] - f2[1], f1[2] - f2[2]) < 50:
                close += 1
    wrist1 = next((x for x in hand1 if x[0] == 0), None)
    wrist2 = next((x for x in hand2 if x[0] == 0), None)
    if wrist1 and wrist2:
        wrist_dist = math.hypot(wrist1[1] - wrist2[1], wrist1[2] - wrist2[2])
        if wrist_dist < 80 and close >= 3:
            return "Clap"

    return None
