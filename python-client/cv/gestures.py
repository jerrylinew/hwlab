"""Gesture classifiers for MediaPipe hand landmarks."""

import mediapipe as mp


HandLandmark = mp.solutions.hands.HandLandmark


def count_extended_fingers(hand_landmarks, handedness_label: str = "Right") -> int:
    """Return how many fingers are extended on one detected hand."""
    landmarks = hand_landmarks.landmark
    fingers_up = 0

    thumb_tip_x = landmarks[HandLandmark.THUMB_TIP].x
    thumb_ip_x = landmarks[HandLandmark.THUMB_IP].x
    if handedness_label == "Right":
        fingers_up += int(thumb_tip_x < thumb_ip_x)
    else:
        fingers_up += int(thumb_tip_x > thumb_ip_x)

    tip_joint_pairs = [
        (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
        (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
        (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP),
    ]
    for tip, pip in tip_joint_pairs:
        fingers_up += int(landmarks[tip].y < landmarks[pip].y)

    return fingers_up


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

    curled_fingers = [
        (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
        (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
        (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP),
    ]
    for tip, pip in curled_fingers:
        if landmarks[tip].y < landmarks[pip].y:
            return False

    knuckle_ys = [
        landmarks[HandLandmark.INDEX_FINGER_MCP].y,
        landmarks[HandLandmark.MIDDLE_FINGER_MCP].y,
        landmarks[HandLandmark.RING_FINGER_MCP].y,
        landmarks[HandLandmark.PINKY_MCP].y,
    ]
    return landmarks[HandLandmark.THUMB_TIP].y < min(knuckle_ys)
