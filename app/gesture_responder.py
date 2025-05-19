import os
import cv2
import time
from glob import glob

# Cache animations in memory
gesture_animations = {}

def load_gesture_animation(gesture_name):
    if gesture_name in gesture_animations:
        return gesture_animations[gesture_name]

    folder = os.path.join("reactions", gesture_name)
    frame_paths = sorted(glob(os.path.join(folder, "frame_*.png")))
    print(f"[DEBUG] Loading frames from: {folder}")
    print(f"[DEBUG] Found {len(frame_paths)} frame(s): {frame_paths}")

    frames = [cv2.imread(p) for p in frame_paths if cv2.imread(p) is not None]
    gesture_animations[gesture_name] = frames
    return frames

def overlay_gesture_animation(base_frame, gesture_name, start_time, duration=2, x=None, y=None, scale=0.4):
    frames = load_gesture_animation(gesture_name)
    if not frames:
        return base_frame

    elapsed = time.time() - start_time
    total_frames = len(frames)
    frame_index = int((elapsed / duration) * total_frames)
    if frame_index >= total_frames:
        return base_frame

    frame = frames[frame_index]
    frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    h, w, _ = frame.shape

    # Position for BOTTOM-LEFT of screen (appears RIGHT in mirrored view)
    if x is None:
        x = 20
    if y is None:
        y = base_frame.shape[0] - h - 20

    # Clamp to keep inside frame boundaries
    x = max(0, min(x, base_frame.shape[1] - w))
    y = max(0, min(y, base_frame.shape[0] - h))

    try:
        base_frame[y:y+h, x:x+w] = frame
    except Exception as e:
        print(f"[ERROR] Failed to overlay image: {e}")

    return base_frame
