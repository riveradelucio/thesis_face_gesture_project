import cv2
import textwrap
from app.config import (
    FONT, FONT_SIZE_SMALL, FONT_THICKNESS,
    COLOR_WHITE
)

def add_user_preview(frame, full_frame, width_ratio=0.2, height_ratio=0.3, padding=10):
    """
    Adds a small preview of the user's camera feed to the bottom-right corner.
    """
    user_view_small = cv2.resize(
        full_frame,
        (int(full_frame.shape[1] * width_ratio), int(full_frame.shape[0] * height_ratio)),
        interpolation=cv2.INTER_AREA
    )

    y_offset = frame.shape[0] - user_view_small.shape[0] - padding
    x_offset = frame.shape[1] - user_view_small.shape[1] - padding

    frame[y_offset:y_offset + user_view_small.shape[0],
          x_offset:x_offset + user_view_small.shape[1]] = user_view_small

    return frame


def add_subtitles(frame, text, max_line_width=45, line_height=25, padding=10):
    """
    Adds wrapped subtitle text to the bottom of the frame with bold outline, no background.
    """
    if not text:
        return frame

    wrapped_lines = textwrap.wrap(text, width=max_line_width)
    subtitle_y = frame.shape[0] - line_height * len(wrapped_lines) - padding

    for i, line in enumerate(wrapped_lines):
        y = subtitle_y + i * line_height

        # Step 1: Draw black outline (shadow)
        cv2.putText(frame, line, (20, y),
                    FONT, FONT_SIZE_SMALL, (0, 0, 0), FONT_THICKNESS + 2)

        # Step 2: Draw white text on top
        cv2.putText(frame, line, (20, y),
                    FONT, FONT_SIZE_SMALL, COLOR_WHITE, FONT_THICKNESS)

    return frame
