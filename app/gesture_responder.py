import os
import cv2
import time
from glob import glob

# Load and store animations in memory
gesture_animations = {}

def load_gesture_animation(gesture_name):
    if gesture_name in gesture_animations:
        return gesture_animations[gesture_name]

    folder = os.path.join("reactions", gesture_name)
    frame_paths = sorted(glob(os.path.join(folder, "frame_*.png")))
    frames = [cv2.imread(p) for p in frame_paths if cv2.imread(p) is not None]
    gesture_animations[gesture_name] = frames
    return frames

# Show animation frames one-by-one over the base frame
def overlay_gesture_animation(base_frame, gesture_name, start_time, duration=2, x=400, y=50, scale=0.5):
    frames = load_gesture_animation(gesture_name)
    if not frames:
        return base_frame

    elapsed = time.time() - start_time
    total_frames = len(frames)
    frame_index = int((elapsed / duration) * total_frames)
    if frame_index >= total_frames:
        return base_frame  # Animation done

    frame = frames[frame_index]
    frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

    h, w, _ = frame.shape
    roi = base_frame[y:y+h, x:x+w]

    # Handle transparency (if needed, otherwise just overlay)
    try:
        blended = cv2.addWeighted(roi, 0.3, frame, 0.7, 0)
        base_frame[y:y+h, x:x+w] = blended
    except:
        pass  # if out of bounds

    return base_frame
