"""Student gesture file.

Run with:
    uvicorn main:app --reload

Change the settings and the small function below to make your own gestures.
"""

from command_block import receive, send, send_when, set_send_to_xiao
from cv import count_extended_fingers, is_thumbs_up
from lab_server import create_app

# True  = send commands to the Vue website and the Seeed Studio XIAO.
# False = send commands only to the Vue website.
SEND_TO_XIAO = True
set_send_to_xiao(SEND_TO_XIAO)


def when_hand_seen(hand):
    """This runs every time the camera sees a hand."""

    # Example: this turns off the XIAO built-in LED when you give a thumbs-up.
    send_when(is_thumbs_up(hand), "thumbs_up")

    # Try your own one-line blocks below:
    # send("hello")
    # send_when(count_extended_fingers(hand) == 5, "open_hand")
    # message_from_vue = receive()


app = create_app(when_hand_seen)
