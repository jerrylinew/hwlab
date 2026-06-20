"""Face detection wrapper around MediaPipe."""

import cv2
import mediapipe as mp


class FaceDetector:
    """Runs MediaPipe face detection with optional frame skipping."""

    def __init__(
        self,
        detection_confidence: float = 0.6,
        process_every_n_frames: int = 1,
    ) -> None:
        self._detector = mp.solutions.face_detection.FaceDetection(
            min_detection_confidence=detection_confidence,
        )
        self._drawing = mp.solutions.drawing_utils
        self._process_every_n_frames = max(1, process_every_n_frames)
        self._frame_count = 0
        self._last_results = None

    def process(self, frame):
        """Process a BGR OpenCV frame and return MediaPipe face results."""
        self._frame_count += 1
        if (
            self._last_results is not None
            and self._frame_count % self._process_every_n_frames != 0
        ):
            return self._last_results

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        self._last_results = self._detector.process(rgb_frame)
        return self._last_results

    def draw(self, frame, results) -> None:
        """Draw face detections onto a BGR OpenCV frame."""
        if not results or not results.detections:
            return
        for detection in results.detections:
            self._drawing.draw_detection(frame, detection)

    def close(self) -> None:
        self._detector.close()
