# Code responsible for producing the latest frame from the camera RTSP stream on a separate thread.
import cv2
import threading
from config import RTSP_STREAM

vcap = cv2.VideoCapture(RTSP_STREAM)
# Local camera, uncomment to enable
# vcap = cv2.VideoCapture(0)

# Variables for RTSP queue
latest_frame = None
last_ret = None
lo = threading.Lock()

def rtsp_cam_buffer(vcap):
    global latest_frame, lo, last_ret

    while True:
        with lo:
            last_ret, latest_frame = vcap.read()

# RTSP Buffer worker thread
threading.Thread(target=rtsp_cam_buffer, args=(vcap,), name="rtsp_read_thread", daemon=True).start()
