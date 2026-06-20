"""Reusable computer-vision helpers for the HW lab server."""

import os

os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "1")

from .acceleration import init_acceleration
from .face_detector import FaceDetector, FaceInfo
from .gestures import classify_gesture, count_extended_fingers, is_thumbs_up
from .hand_detector import HandDetector
from .object_detector import ObjectDetector, ObjectInfo

__all__ = [
    "FaceDetector",
    "FaceInfo",
    "HandDetector",
    "ObjectDetector",
    "ObjectInfo",
    "classify_gesture",
    "count_extended_fingers",
    "init_acceleration",
    "is_thumbs_up",
]
