"""Reusable computer-vision helpers for the HW lab server."""

import os

# "0" tells OpenCV's AVFoundation backend to *request* camera access, which
# pops the native macOS permission dialog on first use. Setting this to "1"
# would skip the request and silently fail until access is granted manually.
os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "0")

import inspect as _inspect

from .acceleration import init_acceleration
from .face_detector import FaceDetector, FaceInfo
from . import gestures as _gestures
from .hand_detector import HandDetector
from .object_detector import ObjectDetector, ObjectInfo

# Make every gesture function defined in gestures.py importable straight from cv
# (e.g. `from cv import is_peace_sign`), so students can add their own gestures in
# gestures.py and use them in main.py WITHOUT ever editing this file. We bind only
# the functions defined in gestures.py — not its imports (math, mediapipe, …) — so
# the cv namespace stays clean, and we introspect the loaded module so it doesn't
# matter where in the file a new gesture is added.
_gesture_exports = [
    _name
    for _name, _obj in _inspect.getmembers(_gestures, _inspect.isfunction)
    if _obj.__module__ == _gestures.__name__ and not _name.startswith("_")
]
for _name in _gesture_exports:
    globals()[_name] = getattr(_gestures, _name)

__all__ = [
    "FaceDetector",
    "FaceInfo",
    "HandDetector",
    "ObjectDetector",
    "ObjectInfo",
    "init_acceleration",
    *_gesture_exports,
]
