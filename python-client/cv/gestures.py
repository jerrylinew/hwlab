"""Gesture classifiers for MediaPipe hand landmarks."""

import math

import mediapipe as mp


HandLandmark = mp.solutions.hands.HandLandmark


def _dist(a, b) -> float:
    """Straight-line distance between two landmarks (in normalized units)."""
    return math.hypot(a.x - b.x, a.y - b.y)


def _extended(landmarks, tip, pip) -> bool:
    """Return True when one finger is extended.

    An extended finger reaches away from the palm, so its tip is the farthest
    point from the wrist. Curl the finger and the tip folds back toward the
    palm, ending up *closer* to the wrist than its own middle (PIP) joint.

    Comparing those two distances — tip-to-wrist vs joint-to-wrist — works no
    matter how the hand is rotated or tilted, unlike comparing raw `y` values.
    """
    wrist = landmarks[HandLandmark.WRIST]
    return _dist(landmarks[tip], wrist) > _dist(landmarks[pip], wrist)


# Each finger as (tip, middle-joint). The thumb uses its IP joint as the
# "middle joint"; the other four use their PIP joint.
_FINGERS = [
    (HandLandmark.THUMB_TIP, HandLandmark.THUMB_IP),
    (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
    (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
    (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
    (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP),
]


def count_extended_fingers(hand_landmarks, handedness_label: str = "Right") -> int:
    """Return how many fingers (0–5) are extended on one detected hand.

    `handedness_label` is accepted for backward compatibility but no longer
    needed — the distance-to-wrist test is the same for either hand.
    """
    landmarks = hand_landmarks.landmark
    return sum(_extended(landmarks, tip, pip) for tip, pip in _FINGERS)


def classify_gesture(fingers_up: int) -> str | None:
    """Classify simple finger-count gestures."""
    if fingers_up == 0:
        return "fist"
    if fingers_up == 5:
        return "open_hand"
    return None


def is_thumbs_up(hand_landmarks) -> bool:
    """Return True when a hand is making a thumbs-up gesture."""
    landmarks = hand_landmarks.landmark

    four_fingers = [
        (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
        (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
        (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP),
    ]

    # 1. The four fingers are curled into a fist (none extended).
    if any(_extended(landmarks, tip, pip) for tip, pip in four_fingers):
        return False

    # 2. The thumb is extended out of the fist.
    if not _extended(landmarks, HandLandmark.THUMB_TIP, HandLandmark.THUMB_IP):
        return False

    # 3. The thumb points UP. "Up" really is up, so here we DO compare the
    #    image `y`: the thumb tip must sit above the row of knuckles.
    knuckle_ys = [
        landmarks[HandLandmark.INDEX_FINGER_MCP].y,
        landmarks[HandLandmark.MIDDLE_FINGER_MCP].y,
        landmarks[HandLandmark.RING_FINGER_MCP].y,
        landmarks[HandLandmark.PINKY_MCP].y,
    ]
    return landmarks[HandLandmark.THUMB_TIP].y < min(knuckle_ys)
