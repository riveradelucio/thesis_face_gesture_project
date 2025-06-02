import cv2
import os
import time
from glob import glob
import numpy as np

gesture_animations = {}

def load_gesture_animation(gesture_name):
    if gesture_name in gesture_animations:
        return gesture_animations[gesture_name]

    folder = os.path.join("reactions", gesture_name)
    frame_paths = sorted(
        glob(os.path.join(folder, "frame_*.png")),
        key=lambda p: int(os.path.splitext(os.path.basename(p))[0].split('_')[-1])
    )
    print(f"[DEBUG] Loading frames from: {folder}")
    print(f"[DEBUG] Found {len(frame_paths)} frame(s): {frame_paths}")

    frames = [cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in frame_paths if cv2.imread(p, cv2.IMREAD_UNCHANGED) is not None]
    gesture_animations[gesture_name] = frames
    return frames

def overlay_gesture_animation(base_frame, gesture_name, start_time, duration=2, x=None, y=None, scale=0.3):
    frames = load_gesture_animation(gesture_name)
    if not frames:
        return base_frame

    elapsed = time.time() - start_time
    total_frames = len(frames)
    frame_index = int((elapsed / duration) * total_frames) % total_frames
    frame = frames[frame_index]

    if frame.shape[2] == 4:
        alpha_channel = frame[:, :, 3] / 255.0
        rgb_frame = frame[:, :, :3]
    else:
        alpha_channel = None
        rgb_frame = frame

    rgb_frame = cv2.resize(rgb_frame, (0, 0), fx=scale, fy=scale)
    h, w, _ = rgb_frame.shape

    base_h, base_w, _ = base_frame.shape

    if x is None:
        x = 80
    if y is None:
        y = base_h // 2 - 100

    x = max(0, min(x, base_w - w))
    y = max(0, min(y, base_h - h))

    try:
        if alpha_channel is not None:
            alpha_channel = cv2.resize(alpha_channel, (w, h))
            for c in range(3):
                base_frame[y:y+h, x:x+w, c] = (
                    alpha_channel * rgb_frame[:, :, c] +
                    (1 - alpha_channel) * base_frame[y:y+h, x:x+w, c]
                ).astype(np.uint8)
        else:
            base_frame[y:y+h, x:x+w] = rgb_frame
    except Exception as e:
        print(f"[ERROR] Failed to overlay image: {e}")

    return base_frame
