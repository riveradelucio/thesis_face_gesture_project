import cv2
import mediapipe as mp
import math

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh()
mp_draw = mp.solutions.drawing_utils

# Landmark indices
finger_tips = [4, 8, 12, 16, 20]
MOUTH_TOP = 13

# Ear clusters
LEFT_EAR_POINTS = [234, 93]
RIGHT_EAR_POINTS = [454, 323]

cap = cv2.VideoCapture(0)

last_gesture = "No Hand Detected"  # Save the last known gesture

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result_hands = hands.process(rgb)
    result_face = face.process(rgb)

    all_hands = []
    mouth_pos = None
    left_ear_positions = []
    right_ear_positions = []

    # Detect face landmarks
    if result_face.multi_face_landmarks:
        for faceLms in result_face.multi_face_landmarks:
            h, w, _ = frame.shape
            for i, lm in enumerate(faceLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)

                if i == MOUTH_TOP:
                    mouth_pos = (cx, cy)

                if i in LEFT_EAR_POINTS:
                    left_ear_positions.append((cx, cy))

                if i in RIGHT_EAR_POINTS:
                    right_ear_positions.append((cx, cy))

    # Detect hand landmarks
    if result_hands.multi_hand_landmarks:
        for handLms in result_hands.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            lm_list = []
            h, w, _ = frame.shape
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))
            all_hands.append(lm_list)

    if all_hands:
        gesture = None  # Start empty

        if len(all_hands) == 1:
            lm_list = all_hands[0]
            fingers = []

            if lm_list[4][2] < lm_list[3][2]:
                fingers.append(1)
            else:
                fingers.append(0)

            for tip_id in finger_tips[1:]:
                if lm_list[tip_id][2] < lm_list[tip_id - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total_fingers = sum(fingers)

            if total_fingers == 0:
                gesture = "Fist"
            elif total_fingers == 2 and fingers[1] == 1 and fingers[2] == 1:
                gesture = "Peace"
            elif total_fingers == 5:
                gesture = "Stop"

            index_finger = next((x for x in lm_list if x[0] == 8), None)

            # Eat gesture
            eat_detected = False
            if mouth_pos:
                index_tip = next((x for x in lm_list if x[0] == 8), None)
                middle_tip = next((x for x in lm_list if x[0] == 12), None)

                if index_tip and middle_tip:
                    fingers_distance = math.hypot(index_tip[1] - middle_tip[1], index_tip[2] - middle_tip[2])

                    avg_x = (index_tip[1] + middle_tip[1]) / 2
                    avg_y = (index_tip[2] + middle_tip[2]) / 2

                    dist_to_mouth = math.hypot(avg_x - mouth_pos[0], avg_y - mouth_pos[1])

                    if fingers_distance < 40 and avg_y > mouth_pos[1] and dist_to_mouth < 100:
                        gesture = "Eat"
                        eat_detected = True

            if not eat_detected and index_finger and mouth_pos:
                dist_to_mouth = math.hypot(index_finger[1] - mouth_pos[0], index_finger[2] - mouth_pos[1])
                if dist_to_mouth < 40:
                    gesture = "Shhh"

            if index_finger:
                for ex, ey in left_ear_positions:
                    dist = math.hypot(index_finger[1] - ex, index_finger[2] - ey)
                    if dist < 40:
                        gesture = "Can't hear (left)"
                        break

                for ex, ey in right_ear_positions:
                    dist = math.hypot(index_finger[1] - ex, index_finger[2] - ey)
                    if dist < 40:
                        gesture = "Can't hear (right)"
                        break

        elif len(all_hands) == 2:
            hand1 = all_hands[0]
            hand2 = all_hands[1]

            # Heart gesture detection
            thumb1 = next((x for x in hand1 if x[0] == 4), None)
            thumb2 = next((x for x in hand2 if x[0] == 4), None)
            pinky1 = next((x for x in hand1 if x[0] == 20), None)
            pinky2 = next((x for x in hand2 if x[0] == 20), None)

            if thumb1 and thumb2 and pinky1 and pinky2:
                thumb_dist = math.hypot(thumb1[1] - thumb2[1], thumb1[2] - thumb2[2])
                pinky_dist = math.hypot(pinky1[1] - pinky2[1], pinky1[2] - pinky2[2])

                if thumb_dist < 60 and pinky_dist < 60:
                    gesture = "Heart"
                else:
                    gesture = None  # reset if thumbs or pinkies move apart



            if not gesture:
                # Medicine gesture fallback
                lowest_point_hand1 = max(hand1, key=lambda x: x[2])
                cv2.circle(frame, (lowest_point_hand1[1], lowest_point_hand1[2]), 10, (0, 255, 0), -1)

                index_tip = next((x for x in hand2 if x[0] == 8), None)
                middle_tip = next((x for x in hand2 if x[0] == 12), None)
                ring_tip = next((x for x in hand2 if x[0] == 16), None)

                touching = False
                if lowest_point_hand1 and (index_tip or middle_tip or ring_tip):
                    if index_tip:
                        dist_index = math.hypot(lowest_point_hand1[1] - index_tip[1], lowest_point_hand1[2] - index_tip[2])
                        if dist_index < 60:
                            touching = True
                    if middle_tip:
                        dist_middle = math.hypot(lowest_point_hand1[1] - middle_tip[1], lowest_point_hand1[2] - middle_tip[2])
                        if dist_middle < 60:
                            touching = True
                    if ring_tip:
                        dist_ring = math.hypot(lowest_point_hand1[1] - ring_tip[1], lowest_point_hand1[2] - ring_tip[2])
                        if dist_ring < 60:
                            touching = True

                if touching:
                    gesture = "Medicine"

        if gesture:
            last_gesture = gesture  # Update last known gesture

    else:
        last_gesture = "No Hand Detected"

    # Show last known gesture
    cv2.putText(frame, last_gesture, (20, 60), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (0, 255, 0), 3)

    cv2.imshow("Gesture Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
