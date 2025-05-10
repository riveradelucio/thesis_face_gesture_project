import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import os
import time

# Load face analysis models (Detection + Recognition)
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])  # Use GPU if available
app.prepare(ctx_id=0)

# Dictionary to store registered face embeddings
KNOWN_FACE_EMBEDDINGS = {}

# Function to compute face embeddings
def get_face_embedding(face_image):
    faces = app.get(face_image)
    if len(faces) > 0:
        return faces[0].embedding  # Extract the face embedding
    return None

# Function to register multiple known faces
def register_known_faces(folder_path):
    if not os.path.exists(folder_path):
        print(f"\u274C Error: Folder '{folder_path}' does not exist. Please create it and add images.")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):  # Supports jpg/png images
            person_name = os.path.splitext(filename)[0]  # Use filename as the person's name
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            if img is None:
                print(f"⚠️ Warning: Could not read image {filename}. Skipping.")
                continue
            embedding = get_face_embedding(img)
            if embedding is not None:
                KNOWN_FACE_EMBEDDINGS[person_name] = embedding
                print(f"✅ Registered {person_name}")

# Ensure the folder exists and register known faces
register_known_faces("known_faces")

# Open webcam
cap = cv2.VideoCapture(0)  # 0 = Default webcam

# Scale factor (adjust for speed vs accuracy)
SCALE_FACTOR = 0.2  # Scale to 50% of original size

print("📹 Webcam is running. Press 'q' to exit.")

# Process video frame-by-frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # End of video

    # Resize the frame (scale down for speed)
    small_frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)

    # Detect faces in the resized frame
    faces = app.get(small_frame)

    for face in faces:
        # Adjust coordinates back to original size
        x, y, x2, y2 = [int(coord / SCALE_FACTOR) for coord in face.bbox]
        embedding = face.embedding  # Extract the face embedding

        # Compare with all known faces (cosine similarity)
        best_match = None
        best_similarity = -1  # Start with lowest similarity

        for name, known_embedding in KNOWN_FACE_EMBEDDINGS.items():
            similarity = np.dot(embedding, known_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(known_embedding))  # Cosine similarity

            if similarity > 0.5:  # Recognition threshold (adjust if needed)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = name

        # Draw bounding box
        color = (0, 255, 0) if best_match else (0, 0, 255)  # Green if recognized, Red if unknown
        cv2.rectangle(frame, (x, y), (x2, y2), color, 2)

        # Add label
        label = best_match if best_match else "Unknown"
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Display the frame
    cv2.imshow("Multi-Person Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
print("✅ Webcam recognition stopped.")