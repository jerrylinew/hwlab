"""Optional object recognition using MediaPipe Objectron."""

from dataclasses import dataclass
from types import SimpleNamespace

import cv2
import mediapipe as mp


@dataclass
class ObjectInfo:
    """Simple object facts for student code."""

    label: str
    raw_object: object


class ObjectDetector:
    """Recognizes one Objectron model: Cup, Shoe, Chair, or Camera."""

    def __init__(
        self,
        model_name: str = "Cup",
        max_objects: int = 2,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
        process_every_n_frames: int = 3,
    ) -> None:
        self.model_name = model_name
        self._objectron_module = getattr(mp.solutions, "objectron", None)
        self._drawing = mp.solutions.drawing_utils
        self._detector = None
        self._process_every_n_frames = max(1, process_every_n_frames)
        self._frame_count = 0
        self._last_results = SimpleNamespace(detected_objects=[], objects=[], available=False)

        if self._objectron_module is not None:
            self._detector = self._objectron_module.Objectron(
                static_image_mode=False,
                max_num_objects=max_objects,
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
                model_name=model_name,
            )

    def process(self, frame):
        """Process a BGR OpenCV frame and return object results."""
        if self._detector is None:
            return self._last_results

        self._frame_count += 1
        if (
            self._last_results.available
            and self._frame_count % self._process_every_n_frames != 0
        ):
            return self._last_results

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        raw_results = self._detector.process(rgb_frame)
        detected_objects = raw_results.detected_objects or []
        self._last_results = SimpleNamespace(
            detected_objects=detected_objects,
            objects=[ObjectInfo(label=self.model_name, raw_object=obj) for obj in detected_objects],
            available=True,
        )
        return self._last_results

    def draw(self, frame, results) -> None:
        if self._detector is None:
            cv2.putText(frame, "Object CV unavailable", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 180, 255), 2)
            return

        for detected_object in getattr(results, "detected_objects", []):
            self._drawing.draw_landmarks(
                frame,
                detected_object.landmarks_2d,
                self._objectron_module.BOX_CONNECTIONS,
            )
            self._drawing.draw_axis(
                frame,
                detected_object.rotation,
                detected_object.translation,
            )
            cv2.putText(frame, self.model_name, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 180, 0), 2)

    def close(self) -> None:
        if self._detector is not None:
            self._detector.close()
