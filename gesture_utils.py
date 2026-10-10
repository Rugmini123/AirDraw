"""
gesture_utils.py
-----------------
Pure, stateless helper functions for interpreting MediaPipe hand landmarks.
No OpenCV drawing calls live here -- just math and classification logic,
which keeps this file easy to test independently of the camera loop.
"""

import config


def is_finger_up(landmarks, tip_idx, pip_idx):
    """
    Returns True if the finger is extended ("up"), False if curled down.

    Uses normalized image coordinates, where y increases downward.
    A finger is considered "up" when its tip is above (smaller y than)
    its own PIP joint -- a simple, robust check that avoids needing
    angle calculations between bones.
    """
    tip_y = landmarks[tip_idx].y
    pip_y = landmarks[pip_idx].y
    return tip_y < pip_y


def get_finger_states(landmarks):
    """
    Returns a dict of booleans describing which fingers are currently up.
    Thumb is intentionally excluded from the gesture state machine --
    its "up" direction depends on hand orientation (left/right hand,
    rotated wrist) and would make the up/down check unreliable, so we
    only rely on it if a future gesture explicitly needs it.
    """
    return {
        "index": is_finger_up(landmarks, config.INDEX_TIP, config.INDEX_PIP),
        "middle": is_finger_up(landmarks, config.MIDDLE_TIP, config.MIDDLE_PIP),
        "ring": is_finger_up(landmarks, config.RING_TIP, config.RING_PIP),
        "pinky": is_finger_up(landmarks, config.PINKY_TIP, config.PINKY_PIP),
    }


def classify_gesture(finger_states):
    """
    Maps a finger-state dict to one of three gesture modes:

    - "draw"   : only the index finger is up -> active drawing pointer
    - "select" : index AND middle are up (peace sign) -> hover/select mode,
                 used to choose colors/tools from the toolbar without drawing
    - "idle"   : any other combination (fist, open palm, etc.) -> pauses
                 drawing entirely, which is what prevents accidental strokes
                 while the user is just repositioning their hand
    """
    index_up = finger_states["index"]
    middle_up = finger_states["middle"]
    ring_up = finger_states["ring"]
    pinky_up = finger_states["pinky"]

    if index_up and middle_up and not ring_up and not pinky_up:
        return "select"

    if index_up and not middle_up and not ring_up and not pinky_up:
        return "draw"

    return "idle"


def get_landmark_pixel_coords(landmarks, landmark_idx, frame_width, frame_height):
    """
    Converts a single MediaPipe landmark's normalized (0.0-1.0) coordinates
    into actual pixel coordinates for the given frame size.
    """
    lm = landmarks[landmark_idx]
    x_px = int(lm.x * frame_width)
    y_px = int(lm.y * frame_height)
    return x_px, y_px