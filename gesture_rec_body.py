import cv2
import time
import numpy as np
import threading
from threading import Lock
import json
import requests
import base64
import queue
import math

from secrets import password

vcap = cv2.VideoCapture("rtsp://admin:" + password + "@192.168.1.14:554")
#vcap = cv2.VideoCapture(0)

protoFile = "body/pose_deploy.prototxt.txt"
weightsFile = "body/pose_iter_584000.caffemodel"

BODY_PARTS = { "RShoulder": 2, "RWrist": 4, "LShoulder": 5 }
colors = [ [0,100,255], [0,100,255], [0,255,255], [0,100,255], [0,255,255], [0,100,255],
         [0,255,0], [255,200,100], [255,0,255], [0,255,0], [255,200,100], [255,0,255],
         [0,0,255], [255,0,0], [200,200,0], [255,0,0], [200,200,0], [0,0,0]]


# Queue for HTTP requests
q = queue.Queue()
def http_queue_worker():
    print("Starting worker")
    while True:
        try:
            item = None
            if q.empty():
                continue

            print("Non empty queue found")

            while not q.empty():
                print("Emptying queue", item)
                item = q.get()
                q.task_done()
            print("Processing last item", item)
            timeDiff = time.time() - item['time']
            if item and timeDiff <= 1:
                print(f'Working on {item}, timeDiff {timeDiff}')
                last_response = requests.post('http://192.168.1.10/volume?delta=' + str(item['value']), timeout=5)
                print(last_response)
                print(f'Finished {item}')
            else:
                print(f'Skipped stale data {item}, timeDiff {timeDiff}')
        except Exception as e:
            print("Failed", e)

# Variables for RTSP queue
latest_frame = None
last_ret = None
lo = Lock()
def rtsp_cam_buffer(vcap):
    global latest_frame, lo, last_ret

    while True:
        with lo:
            last_ret, latest_frame = vcap.read()

# HTTPRequests worker thread
threading.Thread(target=http_queue_worker, daemon=True).start()
# RTSP Buffer worker thread
threading.Thread(target=rtsp_cam_buffer,args=(vcap,),name="rtsp_read_thread", daemon=True).start()

# Create the network
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

while(1):
    start = time.time()
    if (last_ret is not None) and (latest_frame is not None):
        image = latest_frame.copy()
    else:
        time.sleep(0.01)
        continue


    # Fix the CNN input Height and Width based on defaults.
    inHeight = 368
    inWidth = 368

    # Create a resized image for processing
    frameHeight = 720
    frameWidth = int((720/image.shape[0])*image.shape[1])
    image = cv2.resize(image, (frameWidth, frameHeight))
    print(frameWidth, frameHeight)
    
    inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (inWidth, inHeight),
                              (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    
    # Magical lines to drop processing time from 4s -> 0.07s!
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    output = net.forward()

    print("Time Taken in forward pass = {}".format(time.time() - start))

    points = {}
    for part, i in BODY_PARTS.items():
        # Slice heatmap of corresponding body's part.
        heatMap = output[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv2.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / output.shape[3]
        y = (frameHeight * point[1]) / output.shape[2]

        # Add a point if it's confidence is higher than threshold.
        location = (np.array([int(x), int(y)]) if conf > 0.1 else None)
        if location is not None:
            points[part] = location
            cv2.circle(image, (location[0], location[1]), 5, colors[BODY_PARTS[part]%len(colors)], -1, cv2.LINE_AA)

    # If all 3 parts were detected, calculate the linear interpolation value.
    if "LShoulder" not in points or "RShoulder" not in points or "RWrist" not in points:
        continue

    # Draw the enclosing box using LShoulder and top of image
    cv2.rectangle(image, (points["LShoulder"][0], points["LShoulder"][1]), (points["RShoulder"][0], 0), (0, 255, 255), 2) 

    cv2.imshow("Keypoints", image)
    cv2.waitKey(1)
    
    # Vectors for our calculations below
    #             RWrist
    #         /           ↖
    #  vec_L /             \ vec_R
    #      ↙                \
    #   LShoulder ------> RShoulder
    #             vec_Sho
    vec_L = points["LShoulder"] - points["RWrist"]
    vec_R = -points["RShoulder"] + points["RWrist"]
    vec_Sho = points["RShoulder"] - points["LShoulder"]
    normalized_projection =  np.dot(vec_R, vec_Sho) / np.dot(vec_Sho, vec_Sho)

    # If wrist is not above the line, skip
    if (np.cross(vec_R, vec_Sho) > 0):
        continue
    
    # Simply take projection into the volume value.
    volumeDelta = math.ceil(3 * normalized_projection)
    q.put({'value': volumeDelta, 'time': time.time()})
    print("Normalized", normalized_projection)
    print("Volume", volumeDelta)
    print("Total Time Taken in code = {}".format(time.time() - start))
