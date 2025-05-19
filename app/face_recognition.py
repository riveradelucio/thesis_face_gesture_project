import os
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

# Load the face model
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

# Store registered faces
KNOWN_FACE_EMBEDDINGS = {}

# Register known faces from a folder
def register_known_faces(folder_path="known_faces"):
    print(folder_path)
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' not found.")
        return

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".png")):
            name = os.path.splitext(filename)[0].lower()
            img = cv2.imread(os.path.join(folder_path, filename))
            if img is None:
                print(f"⚠️ Could not read {filename}")
                continue
            embedding = get_embedding(img)
            if embedding is not None:
                KNOWN_FACE_EMBEDDINGS[name] = embedding
                print(f"✅ Registered: {name}")

# Get embedding from image
def get_embedding(image):
    faces = app.get(image)
    if len(faces) > 0:
        return faces[0].embedding
    return None

# Detect and recognize faces from a frame
def detect_and_recognize(frame, scale_factor=0.1):
    recognized_faces = []

    small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
    faces = app.get(small_frame)

    for face in faces:
        x1, y1, x2, y2 = [int(coord / scale_factor) for coord in face.bbox]
        embedding = face.embedding

        best_match = None
        best_similarity = -1

        for name, known_embedding in KNOWN_FACE_EMBEDDINGS.items():
            similarity = cosine_similarity(embedding, known_embedding)
            if similarity > 0.5 and similarity > best_similarity:
                best_similarity = similarity
                best_match = name

        recognized_faces.append({
            "bbox": (x1, y1, x2, y2),
            "name": best_match or "Unknown",
            "recognized": bool(best_match)
        })

    return recognized_faces

# Cosine similarity between two vectors
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
