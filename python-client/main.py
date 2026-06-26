"""Student gesture file.

Run with:
    uvicorn main:app --reload

Change the settings and the small function below to make your own gestures.
"""

from command_block import receive, send, send_when, set_send_to_xiao
from cv import count_extended_fingers, is_thumbs_up
from lab_server import create_app

# ─── What Should The Camera Look For? ────────────────────────────────────────

ENABLE_HAND_CV = True
ENABLE_FACE_CV = True
ENABLE_OBJECT_CV = False

# Object CV uses MediaPipe Objectron. Supported models: "Cup", "Shoe", "Chair", "Camera".
OBJECT_MODEL = "Cup"

# True  = send commands to the Vue website and the Seeed Studio XIAO.
# False = send commands only to the Vue website.
SEND_TO_XIAO = False
set_send_to_xiao(SEND_TO_XIAO)


def when_hand_seen(hand):
    """This runs every time the camera sees a hand."""

    # Example: this turns off the XIAO built-in LED when you give a thumbs-up.
    send_when(is_thumbs_up(hand), "thumbs_up")

    # Try your own one-line blocks below:
    # send("hello")
    # send_when(count_extended_fingers(hand) == 5, "open_hand")
    # message_from_vue = receive()


def when_face_seen(face):
    """This runs every time the camera sees a face."""

    # Face examples:
    # send_when(face.mouth_open, "mouth_open")
    # send_when(face.emotion == "happy", "happy")
    # send_when(face.emotion == "surprised", "surprised")
    pass


def when_object_seen(thing):
    """This runs when object CV sees the configured object model."""

    # Object example:
    # send_when(thing.label == "Cup", "cup_seen")
    pass


app = create_app(
    on_hand_seen=when_hand_seen,
    on_face_seen=when_face_seen,
    on_object_seen=when_object_seen,
    enable_hands=ENABLE_HAND_CV,
    enable_faces=ENABLE_FACE_CV,
    enable_objects=ENABLE_OBJECT_CV,
    object_model=OBJECT_MODEL,
)
