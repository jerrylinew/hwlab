"""Face detection and simple expression detection around MediaPipe."""

from dataclasses import dataclass
from types import SimpleNamespace

import cv2
import mediapipe as mp


@dataclass
class FaceInfo:
    """Simple face facts for student code."""

    emotion: str
    mouth_open: bool
    mouth_open_score: float
    smile_score: float
    landmarks: object


class FaceDetector:
    """Runs MediaPipe face detection + face mesh expression checks."""

    def __init__(
        self,
        detection_confidence: float = 0.6,
        process_every_n_frames: int = 1,
    ) -> None:
        self._detector = mp.solutions.face_detection.FaceDetection(
            min_detection_confidence=detection_confidence,
        )
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=0.5,
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
        detections = self._detector.process(rgb_frame)
        mesh_results = self._face_mesh.process(rgb_frame)
        faces = []
        if mesh_results.multi_face_landmarks:
            faces = [self._build_face_info(face_landmarks) for face_landmarks in mesh_results.multi_face_landmarks]

        self._last_results = SimpleNamespace(
            detections=detections.detections if detections else None,
            faces=faces,
            mesh_results=mesh_results,
        )
        return self._last_results

    def draw(self, frame, results) -> None:
        """Draw face detections onto a BGR OpenCV frame."""
        if not results or not results.detections:
            detections = []
        else:
            detections = results.detections

        for detection in detections:
            self._drawing.draw_detection(frame, detection)

        for index, face in enumerate(getattr(results, "faces", [])):
            y = 30 + index * 28
            text = f"face: {face.emotion} mouth_open={face.mouth_open}"
            cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

    def close(self) -> None:
        self._detector.close()
        self._face_mesh.close()

    @staticmethod
    def _build_face_info(face_landmarks) -> FaceInfo:
        landmarks = face_landmarks.landmark
        mouth_top = landmarks[13]
        mouth_bottom = landmarks[14]
        mouth_left = landmarks[61]
        mouth_right = landmarks[291]
        face_left = landmarks[234]
        face_right = landmarks[454]

        mouth_width = max(abs(mouth_right.x - mouth_left.x), 0.001)
        face_width = max(abs(face_right.x - face_left.x), 0.001)
        mouth_open_score = abs(mouth_bottom.y - mouth_top.y) / mouth_width
        smile_score = mouth_width / face_width
        mouth_open = mouth_open_score > 0.12

        if mouth_open_score > 0.20:
            emotion = "surprised"
        elif smile_score > 0.38 and not mouth_open:
            emotion = "happy"
        else:
            emotion = "neutral"

        return FaceInfo(
            emotion=emotion,
            mouth_open=mouth_open,
            mouth_open_score=mouth_open_score,
            smile_score=smile_score,
            landmarks=face_landmarks,
        )
