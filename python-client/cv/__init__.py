"""Reusable computer-vision helpers for the HW lab server."""

import os

# "0" tells OpenCV's AVFoundation backend to *request* camera access, which
# pops the native macOS permission dialog on first use. Setting this to "1"
# would skip the request and silently fail until access is granted manually.
os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "0")

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
