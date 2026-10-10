"""
config.py
----------
Central place for every constant used across AirDraw.
Keeping these here means we can tune sensitivity, colors, or layout
without touching the actual logic files.
"""

# ---------------------------------------------------------------------------
# Camera settings
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0
CAMERA_BACKEND = "CAP_DSHOW"   # This machine's webcam only opens reliably via DirectShow.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# ---------------------------------------------------------------------------
# MediaPipe Hands settings
# ---------------------------------------------------------------------------
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# ---------------------------------------------------------------------------
# Landmark indices we care about (MediaPipe's 21-point hand model)
# ---------------------------------------------------------------------------
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18
THUMB_TIP = 4
THUMB_IP = 3
WRIST = 0

# ---------------------------------------------------------------------------
# Drawing behaviour
# ---------------------------------------------------------------------------
BRUSH_THICKNESS = 8
ERASER_THICKNESS = 40
SMOOTHING_WINDOW = 5          # number of past points averaged to reduce jitter
HOVER_SELECT_FRAMES = 15      # frames the fingertip must dwell on a toolbar icon to select it

# ---------------------------------------------------------------------------
# Colors (B, G, R) -- OpenCV uses BGR ordering, not RGB
# ---------------------------------------------------------------------------
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)        # canvas background / eraser "color"

# Toolbar swatches, in the order they'll be drawn left-to-right
TOOL_COLORS = {
    "RED": COLOR_RED,
    "GREEN": COLOR_GREEN,
    "BLUE": COLOR_BLUE,
    "YELLOW": COLOR_YELLOW,
    "WHITE": COLOR_WHITE,
}

# ---------------------------------------------------------------------------
# Toolbar layout
# ---------------------------------------------------------------------------
TOOLBAR_HEIGHT = 80
SWATCH_SIZE = 60
SWATCH_MARGIN = 20
SWATCH_START_X = 20

# ---------------------------------------------------------------------------
# Keyboard shortcuts (backup controls)
# ---------------------------------------------------------------------------
KEY_RED = ord("r")
KEY_GREEN = ord("g")
KEY_BLUE = ord("b")
KEY_YELLOW = ord("y")
KEY_WHITE = ord("w")
KEY_ERASER = ord("e")
KEY_CLEAR = ord("c")
KEY_UNDO = ord("z")
KEY_REDO = ord("x")
KEY_QUIT = ord("q")

# ---------------------------------------------------------------------------
# Undo/redo behaviour
# ---------------------------------------------------------------------------
MAX_UNDO_STEPS = 15   # cap history depth so memory usage stays bounded