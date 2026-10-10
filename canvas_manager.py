"""
canvas_manager.py
-------------------
Owns the persistent drawing canvas and all state related to color, tool
selection, and stroke continuity. This is the single source of truth for
"what's currently on the canvas" and "what tool is active" -- both the
gesture path and the keyboard-shortcut path call into this same class,
so behaviour never diverges between the two input methods.
"""

import numpy as np
import cv2

import config


class CanvasManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # The persistent drawing surface. Starts fully black/transparent;
        # strokes accumulate here across frames.
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)

        # Current tool state. "color" holds the actual BGR tuple in use;
        # "is_eraser" flags whether we're erasing rather than drawing.
        self.current_color_name = "WHITE"
        self.current_color = config.TOOL_COLORS["WHITE"]
        self.is_eraser = False

        # Tracks the last fingertip position so we can draw a continuous
        # line segment from the previous point to the current one. None
        # means "no previous point" -- e.g. right after lifting the hand,
        # so we don't draw a stray line jumping across the canvas.
        self.prev_point = None

        # Undo/redo history. We snapshot the canvas at the *start* of each
        # new stroke (and before a clear), never mid-stroke -- this keeps
        # one undo step equal to one whole stroke or one clear, which
        # matches how a user thinks about "undo" rather than undoing a
        # handful of pixels at a time.
        self.undo_stack = []
        self.redo_stack = []

    def set_color(self, color_name):
        """Switches to a named drawing color and turns off eraser mode."""
        if color_name not in config.TOOL_COLORS:
            return
        self.current_color_name = color_name
        self.current_color = config.TOOL_COLORS[color_name]
        self.is_eraser = False

    def set_eraser(self):
        """Switches to eraser mode. Internally this just draws in the
        canvas's background color, so no special-case drawing code is
        needed elsewhere -- the eraser is "just another color" as far as
        the line-drawing logic is concerned."""
        self.is_eraser = True
        self.current_color_name = "ERASER"

    def clear(self):
        """Wipes the canvas back to blank. Also resets prev_point so a
        stray line doesn't connect across the clear operation."""
        self._push_undo_snapshot()
        self.canvas[:] = 0
        self.prev_point = None

    def _push_undo_snapshot(self):
        """
        Records the canvas's current pixels onto the undo stack, before
        a stroke or a clear is about to change it. Any new action
        invalidates the redo stack -- once you draw something new after
        undoing, there's no longer a consistent "future" to redo into.
        """
        self.undo_stack.append(self.canvas.copy())
        if len(self.undo_stack) > config.MAX_UNDO_STEPS:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        """
        Reverts the canvas to its state before the most recent stroke or
        clear. Does nothing if there's no history yet. The current state
        is pushed onto the redo stack first, so redo() can bring it back.
        """
        if not self.undo_stack:
            return
        self.redo_stack.append(self.canvas.copy())
        self.canvas = self.undo_stack.pop()
        self.prev_point = None

    def redo(self):
        """
        Re-applies a stroke or clear that was just undone. Does nothing
        if there's nothing to redo (e.g. you haven't undone anything, or
        you've since drawn something new, which clears this stack).
        """
        if not self.redo_stack:
            return
        self.undo_stack.append(self.canvas.copy())
        self.canvas = self.redo_stack.pop()
        self.prev_point = None

    def reset_stroke(self):
        """Call this whenever the gesture leaves 'draw' mode, so the next
        time drawing resumes it starts a fresh line instead of connecting
        back to wherever the fingertip last was."""
        self.prev_point = None

    def draw_to(self, point):
        """
        Draws a line segment from the last recorded point to the given
        point, then updates the last-point tracker. If there is no
        previous point (fresh stroke), just records the current point
        without drawing -- a line needs two points, and drawing from a
        None origin would produce nonsensical dot artifacts.
        """
        thickness = config.ERASER_THICKNESS if self.is_eraser else config.BRUSH_THICKNESS
        draw_color = config.COLOR_BLACK if self.is_eraser else self.current_color

        if self.prev_point is None:
            # This is the first point of a brand new stroke -- snapshot
            # the canvas now, before any pixels change, so undo() can
            # restore exactly this pre-stroke state later.
            self._push_undo_snapshot()
        else:
            cv2.line(self.canvas, self.prev_point, point, draw_color, thickness, cv2.LINE_AA)

        self.prev_point = point

    def get_display_label(self):
        """Returns a short string describing the active tool, for the
        on-screen status overlay (e.g. 'ERASER' or 'WHITE')."""
        return "ERASER" if self.is_eraser else self.current_color_name

    def composite_onto(self, frame_bgr):
        """
        Merges the persistent canvas onto the live camera frame, in place,
        so strokes appear to float over the webcam feed. Uses a mask so
        only the drawn (non-black) pixels of the canvas overwrite the
        frame -- everywhere else, the live camera feed shows through
        untouched.
        """
        gray_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        background = cv2.bitwise_and(frame_bgr, frame_bgr, mask=mask_inv)
        foreground = cv2.bitwise_and(self.canvas, self.canvas, mask=mask)

        combined = cv2.add(background, foreground)
        frame_bgr[:] = combined