"""
hand_tracker.py
-----------------
Wraps MediaPipe Hands so the rest of the app never touches the MediaPipe
API directly. If detection settings ever need tuning, or the underlying
library changes, this is the only file that should need edits.
"""

import cv2
import mediapipe as mp

import config


class HandTracker:
    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_drawing_styles = mp.solutions.drawing_styles

        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )

    def process(self, frame_bgr):
        """
        Runs hand detection on a single BGR frame (as read from OpenCV).
        Returns the raw MediaPipe results object, which callers use to
        pull out landmarks via get_first_hand_landmarks().

        MediaPipe expects RGB input, so we convert here -- callers should
        never need to think about color-space conversion themselves.
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self._hands.process(frame_rgb)
        return results

    def get_first_hand_landmarks(self, results):
        """
        Returns the landmark list for the first detected hand, or None if
        no hand is currently visible in frame. We only ever look at the
        first hand since config.MAX_NUM_HANDS is 1 for this project.
        """
        if not results.multi_hand_landmarks:
            return None
        return results.multi_hand_landmarks[0].landmark

    def draw_landmarks(self, frame_bgr, results):
        """
        Draws the hand skeleton (landmarks + connections) directly onto
        the given frame, in place. Satisfies the requirement to visually
        show hand tracking to the user for feedback/debugging.
        """
        if not results.multi_hand_landmarks:
            return

        for hand_landmarks in results.multi_hand_landmarks:
            self._mp_drawing.draw_landmarks(
                frame_bgr,
                hand_landmarks,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_drawing_styles.get_default_hand_landmarks_style(),
                self._mp_drawing_styles.get_default_hand_connections_style(),
            )

    def close(self):
        """Releases MediaPipe's internal resources. Call on app shutdown."""
        self._hands.close()