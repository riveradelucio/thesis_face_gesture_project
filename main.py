import cv2
import time
import os
from app.face_recognition import detect_and_recognize, register_known_faces
from app.hi_wave_detector import detect_wave
from app.gesture_recognition import detect_custom_gesture
from app.gesture_responder import overlay_gesture_animation

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Cannot access webcam.")
        return

    register_known_faces("known_faces")

    frame_count = 0
    faces = []
    interaction_started = False
    interaction_start_time = None
    show_wave_message_duration = 2  # seconds
    gesture_start_delay = 2         # ⏱️ wait 2 seconds after wave before detecting gestures

    last_gesture = None
    gesture_last_time = 0
    gesture_display_duration = 2  # seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        current_time = time.time()

        # Step 1: Face recognition every 3 frames
        if frame_count % 3 == 0:
            faces = detect_and_recognize(frame, scale_factor=0.3)

        # Step 2: Draw recognized faces
        for face in faces:
            x1, y1, x2, y2 = face["bbox"]
            label = face["name"]
            color = (0, 180, 0) if face["recognized"] else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Step 3: Wave trigger
        recognized = any(face["recognized"] for face in faces)

        if recognized and not interaction_started:
            if detect_wave(frame):
                print("Wave Detected! Interaction Started.")
                interaction_started = True
                interaction_start_time = current_time

        # Step 4: Show "Hi detected" message
        if interaction_start_time and current_time - interaction_start_time < show_wave_message_duration:
            cv2.putText(frame, "Hi detected!", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 100, 0), 3)

        # Step 5: Gesture Recognition with delay
        if interaction_started and current_time - interaction_start_time >= gesture_start_delay:
            cv2.putText(frame, "Interaction Running...", (20, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (280, 180, 180), 2)

            gesture = detect_custom_gesture(frame)

            if gesture and (gesture != last_gesture or current_time - gesture_last_time > gesture_display_duration):
                print(f"Detected gesture: {gesture}")
                last_gesture = gesture
                gesture_last_time = current_time

            # Step 6: Show gesture icon
            if last_gesture and current_time - gesture_last_time < gesture_display_duration:
                frame = overlay_gesture_animation(
                    frame,
                    last_gesture,
                    gesture_last_time,
                    duration=gesture_display_duration,
                    x=20,
                    y=300,
                    scale=0.2
                )

        # Final camera feed
        cv2.imshow("Face + Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
