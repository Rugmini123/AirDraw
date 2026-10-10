/**
 * config.js
 * ----------
 * Central place for every constant used across the AirDraw web app.
 * Mirrors the structure of the Python version's config.py, so anything
 * you already understand there carries over directly here.
 */

export const CONFIG = {
  // -------------------------------------------------------------------
  // Camera settings
  // -------------------------------------------------------------------
  FRAME_WIDTH: 1280,
  FRAME_HEIGHT: 720,

  // -------------------------------------------------------------------
  // MediaPipe HandLandmarker settings
  // -------------------------------------------------------------------
  MAX_NUM_HANDS: 1,
  MIN_DETECTION_CONFIDENCE: 0.7,
  MIN_TRACKING_CONFIDENCE: 0.7,

  // -------------------------------------------------------------------
  // Landmark indices (MediaPipe's 21-point hand model -- same numbering
  // as the Python "solutions" API, so this maps 1:1 to gesture_utils.py)
  // -------------------------------------------------------------------
  INDEX_TIP: 8,
  INDEX_PIP: 6,
  MIDDLE_TIP: 12,
  MIDDLE_PIP: 10,
  RING_TIP: 16,
  RING_PIP: 14,
  PINKY_TIP: 20,
  PINKY_PIP: 18,
  THUMB_TIP: 4,
  THUMB_IP: 3,
  WRIST: 0,

  // -------------------------------------------------------------------
  // Drawing behaviour
  // -------------------------------------------------------------------
  BRUSH_THICKNESS: 8,
  ERASER_THICKNESS: 40,
  SMOOTHING_WINDOW: 5,
  HOVER_SELECT_FRAMES: 15,
  MAX_UNDO_STEPS: 15,

  // -------------------------------------------------------------------
  // Colors -- plain CSS color strings here instead of BGR tuples,
  // since Canvas 2D (like all web APIs) works in normal RGB/CSS color
  // notation, not OpenCV's BGR ordering.
  // -------------------------------------------------------------------
  COLOR_RED: "#FF0000",
  COLOR_GREEN: "#00C853",
  COLOR_BLUE: "#2979FF",
  COLOR_YELLOW: "#FFD600",
  COLOR_WHITE: "#FFFFFF",
  COLOR_BACKGROUND: "#000000",

  TOOL_COLORS: {
    RED: "#FF0000",
    GREEN: "#00C853",
    BLUE: "#2979FF",
    YELLOW: "#FFD600",
    WHITE: "#FFFFFF",
  },

  // -------------------------------------------------------------------
  // Toolbar layout
  // -------------------------------------------------------------------
  TOOLBAR_HEIGHT: 80,
  SWATCH_SIZE: 60,
  SWATCH_MARGIN: 20,
  SWATCH_START_X: 20,
};