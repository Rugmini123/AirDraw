"""
main.py
--------
AirDraw entry point. Ties together webcam capture, hand tracking, gesture
classification, canvas drawing, and the UI overlay into a single real-time
loop.

Run with:  python main.py
Quit with: press 'q', or close the window.
"""

import cv2

import config
from hand_tracker import HandTracker
from canvas_manager import CanvasManager
import gesture_utils
import ui_overlay


def open_camera():
    """
    Opens the webcam using the backend this project's dev machine needs.
    cv2.CAP_DSHOW is required here -- plain cv2.VideoCapture(0) reliably
    fails to open the camera on this setup, even though the same index
    works fine through the Windows Camera app and through DSHOW directly.
    """
    cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    return cap


def smooth_point(history, new_point):
    """
    Maintains a rolling window of recent fingertip positions and returns
    their average. This is what keeps drawn lines smooth instead of
    jittery -- raw landmark positions jump slightly frame-to-frame even
    when your hand is steady, and averaging irons that out.
    """
    history.append(new_point)
    if len(history) > config.SMOOTHING_WINDOW:
        history.pop(0)

    avg_x = int(sum(p[0] for p in history) / len(history))
    avg_y = int(sum(p[1] for p in history) / len(history))
    return avg_x, avg_y


def main():
    cap = open_camera()
    if not cap.isOpened():
        print("ERROR: Could not open webcam. Check camera connection/permissions.")
        return

    tracker = HandTracker()
    canvas = CanvasManager(config.FRAME_WIDTH, config.FRAME_HEIGHT)

    point_history = []          # rolling window for smoothing the pointer
    hover_label = None          # which toolbar item is currently being hovered
    hover_counter = 0            # how many consecutive frames it's been hovered

    print("AirDraw running. Press 'q' to quit.")

    while True:
        success, frame = cap.read()
        if not success:
            print("WARNING: Failed to read frame from webcam.")
            break

        # Mirror the frame so movement feels natural (like a mirror), and
        # resize to our configured working resolution in case the camera
        # driver ignored our requested capture size.
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))

        results = tracker.process(frame)
        landmarks = tracker.get_first_hand_landmarks(results)

        if landmarks is None:
            # No hand visible -- treat like idle: stop any in-progress
            # stroke so a stray line doesn't appear once the hand returns.
            canvas.reset_stroke()
            hover_label = None
            hover_counter = 0
        else:
            finger_states = gesture_utils.get_finger_states(landmarks)
            gesture = gesture_utils.classify_gesture(finger_states)

            index_x, index_y = gesture_utils.get_landmark_pixel_coords(
                landmarks, config.INDEX_TIP, config.FRAME_WIDTH, config.FRAME_HEIGHT
            )
            smoothed_point = smooth_point(point_history, (index_x, index_y))

            if gesture == "draw":
                # Only the index finger is up -- actively drawing.
                # Skip drawing while the fingertip is over the toolbar
                # strip itself, so you don't accidentally paint over the
                # UI while reaching for a color.
                if smoothed_point[1] > config.TOOLBAR_HEIGHT:
                    canvas.draw_to(smoothed_point)
                else:
                    canvas.reset_stroke()
                hover_label = None
                hover_counter = 0

            elif gesture == "select":
                # Index + middle up -- hovering to pick a tool, not drawing.
                canvas.reset_stroke()
                new_hover = ui_overlay.get_hovered_item(smoothed_point[0], smoothed_point[1])

                if new_hover == hover_label and new_hover is not None:
                    hover_counter += 1
                else:
                    hover_label = new_hover
                    hover_counter = 1 if new_hover is not None else 0

                if hover_label is not None and hover_counter >= config.HOVER_SELECT_FRAMES:
                    if hover_label == "CLEAR":
                        canvas.clear()
                    elif hover_label == "ERASER":
                        canvas.set_eraser()
                    else:
                        canvas.set_color(hover_label)
                    hover_counter = 0  # require a fresh dwell before re-triggering

            else:
                # Idle -- any other hand shape (fist, open palm, etc.)
                canvas.reset_stroke()
                hover_label = None
                hover_counter = 0

            # Draw the skeleton overlay and fingertip pointer for feedback.
            tracker.draw_landmarks(frame, results)
            ui_overlay.draw_pointer(
                frame, smoothed_point, canvas.current_color, canvas.is_eraser
            )

        # Merge the persistent canvas onto this frame, then draw UI on top.
        canvas.composite_onto(frame)

        hover_progress = (
            hover_counter / config.HOVER_SELECT_FRAMES if hover_label is not None else 0.0
        )
        ui_overlay.draw_toolbar(frame, hovered_label=hover_label, hover_progress=hover_progress)
        ui_overlay.draw_status(frame, canvas.get_display_label())

        cv2.imshow("AirDraw", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == config.KEY_QUIT:
            break
        elif key == config.KEY_RED:
            canvas.set_color("RED")
        elif key == config.KEY_GREEN:
            canvas.set_color("GREEN")
        elif key == config.KEY_BLUE:
            canvas.set_color("BLUE")
        elif key == config.KEY_YELLOW:
            canvas.set_color("YELLOW")
        elif key == config.KEY_WHITE:
            canvas.set_color("WHITE")
        elif key == config.KEY_ERASER:
            canvas.set_eraser()
        elif key == config.KEY_CLEAR:
            canvas.clear()
        elif key == config.KEY_UNDO:
            canvas.undo()
        elif key == config.KEY_REDO:
            canvas.redo()

    cap.release()
    tracker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()