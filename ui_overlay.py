"""
ui_overlay.py
--------------
Everything cosmetic lives here: the toolbar of color/tool swatches, the
hover-highlight feedback while selecting, and the status text showing the
active tool. Keeping this separate from gesture/canvas logic means the
UI can be redesigned without touching how drawing or selection actually
work.
"""

import cv2

import config


def _get_toolbar_items():
    """
    Builds an ordered list of toolbar items: each color swatch, plus the
    ERASER and CLEAR icons at the end. Each item is a dict describing its
    label, its BGR color (for drawing the swatch), and its x-range on
    screen -- computed once per call so the layout logic lives in exactly
    one place.
    """
    items = []
    x = config.SWATCH_START_X

    for name, color in config.TOOL_COLORS.items():
        items.append({
            "label": name,
            "color": color,
            "x_start": x,
            "x_end": x + config.SWATCH_SIZE,
        })
        x += config.SWATCH_SIZE + config.SWATCH_MARGIN

    # ERASER swatch: rendered as a dark gray box with a label, since it
    # has no natural "color" of its own.
    items.append({
        "label": "ERASER",
        "color": (60, 60, 60),
        "x_start": x,
        "x_end": x + config.SWATCH_SIZE,
    })
    x += config.SWATCH_SIZE + config.SWATCH_MARGIN

    # CLEAR swatch: distinct dark red box to signal a destructive action.
    items.append({
        "label": "CLEAR",
        "color": (30, 30, 150),
        "x_start": x,
        "x_end": x + config.SWATCH_SIZE,
    })

    return items


def get_hovered_item(x, y):
    """
    Given a fingertip's pixel position, returns the toolbar item's label
    if the point falls within the toolbar strip and inside a swatch's
    bounds, or None otherwise. main.py calls this every frame while in
    'select' gesture mode to figure out what the user is hovering over.
    """
    if y < 0 or y > config.TOOLBAR_HEIGHT:
        return None

    for item in _get_toolbar_items():
        if item["x_start"] <= x <= item["x_end"]:
            return item["label"]

    return None


def _text_color_for(bgr_color):
    """
    Picks black or white text depending on how bright the given BGR color
    is, using standard perceived-luminance weighting. This keeps every
    swatch's label readable regardless of how light or dark that swatch's
    color happens to be -- e.g. black text on WHITE/YELLOW, white text on
    BLUE/dark-gray/dark-red.
    """
    b, g, r = bgr_color
    luminance = (0.114 * b) + (0.587 * g) + (0.299 * r)
    return (0, 0, 0) if luminance > 150 else (255, 255, 255)


def draw_toolbar(frame_bgr, hovered_label=None, hover_progress=0.0):
    """
    Draws the toolbar strip across the top of the frame, with each
    swatch, a readable text label on every swatch (including ERASER and
    CLEAR, which have no natural color of their own), plus a progress
    indicator on whichever swatch is currently being hovered.
    """
    height, width = frame_bgr.shape[:2]

    # Toolbar background strip
    cv2.rectangle(frame_bgr, (0, 0), (width, config.TOOLBAR_HEIGHT), (40, 40, 40), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.45
    font_thickness = 1

    for item in _get_toolbar_items():
        top_left = (item["x_start"], config.SWATCH_MARGIN // 2)
        bottom_right = (item["x_end"], config.SWATCH_MARGIN // 2 + config.SWATCH_SIZE)

        cv2.rectangle(frame_bgr, top_left, bottom_right, item["color"], -1)

        # White border, thicker if this swatch is currently selected/hovered
        border_thickness = 2
        if item["label"] == hovered_label:
            border_thickness = 4
        cv2.rectangle(frame_bgr, top_left, bottom_right, (255, 255, 255), border_thickness)

        # Text label, centered inside the swatch, with contrast-aware color
        # so it stays readable on every swatch color (including ERASER's
        # dark gray and CLEAR's dark red, which previously had no label
        # at all).
        text_color = _text_color_for(item["color"])
        (text_w, text_h), _ = cv2.getTextSize(item["label"], font, font_scale, font_thickness)
        swatch_center_x = (item["x_start"] + item["x_end"]) // 2
        swatch_center_y = (top_left[1] + bottom_right[1]) // 2
        text_x = swatch_center_x - text_w // 2
        text_y = swatch_center_y + text_h // 2
        cv2.putText(
            frame_bgr,
            item["label"],
            (text_x, text_y),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

        # Hover progress bar: a thin white bar along the bottom edge of the
        # swatch that fills left-to-right as dwell time accumulates.
        if item["label"] == hovered_label and hover_progress > 0:
            bar_width = int((item["x_end"] - item["x_start"]) * hover_progress)
            bar_y = bottom_right[1] + 4
            cv2.line(
                frame_bgr,
                (item["x_start"], bar_y),
                (item["x_start"] + bar_width, bar_y),
                (255, 255, 255),
                3,
            )


def draw_status(frame_bgr, tool_label):
    """
    Draws a small status readout in the corner showing the currently
    active tool/color, so the user always knows what they're about to
    draw with without checking the toolbar.
    """
    height, width = frame_bgr.shape[:2]
    text = f"Tool: {tool_label}"

    cv2.putText(
        frame_bgr,
        text,
        (width - 260, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


def draw_pointer(frame_bgr, point, color, is_eraser=False):
    """
    Draws a small circle at the current fingertip position, giving the
    user a clear visual anchor for where their "pen" currently is.
    """
    radius = config.ERASER_THICKNESS // 2 if is_eraser else 8
    cv2.circle(frame_bgr, point, radius, color, 2, cv2.LINE_AA)