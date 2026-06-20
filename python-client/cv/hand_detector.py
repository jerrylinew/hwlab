"""Hand detection wrapper around MediaPipe."""

import cv2
import mediapipe as mp


class HandDetector:
    """Runs MediaPipe hand landmark detection with optional frame skipping."""

    def __init__(
        self,
        max_hands: int = 2,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.6,
        model_complexity: int = 0,
        process_every_n_frames: int = 1,
    ) -> None:
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=max_hands,
            model_complexity=model_complexity,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self._drawing = mp.solutions.drawing_utils
        self._connections = mp.solutions.hands.HAND_CONNECTIONS
        self._process_every_n_frames = max(1, process_every_n_frames)
        self._frame_count = 0
        self._last_results = None

    def process(self, frame):
        """Process a BGR OpenCV frame and return MediaPipe hand results."""
        self._frame_count += 1
        if (
            self._last_results is not None
            and self._frame_count % self._process_every_n_frames != 0
        ):
            return self._last_results

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        self._last_results = self._hands.process(rgb_frame)
        return self._last_results

    def draw(self, frame, results) -> None:
        """Draw hand landmarks onto a BGR OpenCV frame."""
        if not results or not results.multi_hand_landmarks:
            return
        for hand_landmarks in results.multi_hand_landmarks:
            self._drawing.draw_landmarks(frame, hand_landmarks, self._connections)

    def close(self) -> None:
        self._hands.close()
