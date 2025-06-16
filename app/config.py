import cv2
import os

# ==========================
# Font Settings
# ==========================

FONT = cv2.FONT_HERSHEY_SIMPLEX

# Font Sizes
FONT_SIZE_SMALL = 0.45
FONT_SIZE_MEDIUM = 0.6
FONT_SIZE_LARGE = 1.0

# Font Thickness
FONT_THICKNESS = 1

# ==========================
# Color Definitions (BGR)
# ==========================

COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_GRAY = (200, 200, 200)
COLOR_PINK = (280, 180, 180)  # Slightly out of standard range, still visible

# ==========================
# UI Window Settings
# ==========================

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
WINDOW_NAME = "Face + Gesture Recognition"

# ==========================
# Animation & Gesture Timing
# ==========================

IDLE_ANIMATION_NAME = "Idle_state"
IDLE_ANIMATION_DURATION = 2.5
GESTURE_DISPLAY_DURATION = 2
GESTURE_START_DELAY = 2
SHOW_WAVE_MESSAGE_DURATION = 4.5

# ==========================
# Recognition Settings
# ==========================

RECOGNITION_TIMEOUT = 5  # Seconds to wait before prompting wave

# ==========================
# Global Background Image
# ==========================

BACKGROUND_PATH = r"C:\Users\river\OneDrive - Radboud Universiteit\Documenten\GitHub\thesis_face_gesture_project\reactions\Background\house.png"

RAW_BACKGROUND = cv2.imread(BACKGROUND_PATH)

if RAW_BACKGROUND is None:
    raise FileNotFoundError(f"❌ Background image not found at: {BACKGROUND_PATH}")
