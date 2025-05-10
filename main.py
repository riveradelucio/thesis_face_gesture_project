import cv2
from app.face_recognition import detect_and_recognize, register_known_faces

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Cannot access webcam.")
        return

    # Load known faces once
    register_known_faces("known_faces")

    # Track frames for skipping
    frame_count = 0
    faces = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Only detect and recognize every 3rd frame
        if frame_count % 3 == 0:
            faces = detect_and_recognize(frame, scale_factor=0.3)

        # Draw face results from last detection
        for face in faces:
            x1, y1, x2, y2 = face["bbox"]
            label = face["name"]
            color = (0, 255, 0) if face["recognized"] else (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

