import cv2
import time
import numpy as np
import threading
from threading import Lock
#vcap = cv2.VideoCapture("rtsp://admin:test1234@192.168.1.14:554")
vcap = cv2.VideoCapture(0)
cv2.namedWindow('VIDEO', cv2.WINDOW_NORMAL)
cv2.resizeWindow('VIDEO', 600, 600)
protoFile = "body/pose_deploy.prototxt.txt"
weightsFile = "body/pose_iter_584000.caffemodel"
nPoints = 22

latest_frame = None
last_ret = None
lo = Lock()
import csv
import datetime

    
import json
import requests
import base64

import pyttsx3
engine = pyttsx3.init()
nPoints = 18
# COCO Output Format
keypointsMapping = ['Nose', 'Neck', 'R-Sho', 'R-Elb', 'R-Wr', 'L-Sho', 'L-Elb', 'L-Wr', 'R-Hip', 'R-Knee', 'R-Ank', 'L-Hip', 'L-Knee', 'L-Ank', 'R-Eye', 'L-Eye', 'R-Ear', 'L-Ear']

POSE_PAIRS = [[1,2], [1,5], [2,3], [3,4], [5,6], [6,7],
              [1,8], [8,9], [9,10], [1,11], [11,12], [12,13],
              [1,0], [0,14], [14,16], [0,15], [15,17],
              [2,17], [5,16] ]

# index of pafs correspoding to the POSE_PAIRS
# e.g for POSE_PAIR(1,2), the PAFs are located at indices (31,32) of output, Similarly, (1,5) -> (39,40) and so on.
mapIdx = [[31,32], [39,40], [33,34], [35,36], [41,42], [43,44],
          [19,20], [21,22], [23,24], [25,26], [27,28], [29,30],
          [47,48], [49,50], [53,54], [51,52], [55,56],
          [37,38], [45,46]]

colors = [ [0,100,255], [0,100,255], [0,255,255], [0,100,255], [0,255,255], [0,100,255],
         [0,255,0], [255,200,100], [255,0,255], [0,255,0], [255,200,100], [255,0,255],
         [0,0,255], [255,0,0], [200,200,0], [255,0,0], [200,200,0], [0,0,0]]

import queue

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
                last_response = requests.post('http://192.168.1.10/volume?delta=' + str(item['value']), timeout=3)
                print(last_response)
                print(f'Finished {item}')
            else:
                print(f'Skipped stale data {item}, timeDiff {timeDiff}')
        except Exception as e:
            print("Failed", e)

def rtsp_cam_buffer(vcap):
    global latest_frame, lo, last_ret

    while True:
        with lo:
            last_ret, latest_frame = vcap.read()

# HTTPRequests worker thread
threading.Thread(target=http_queue_worker, daemon=True).start()
# RTSP Buffer worker thread
threading.Thread(target=rtsp_cam_buffer,args=(vcap,),name="rtsp_read_thread", daemon=True).start()

while(1):
    start = time.time()
    if (last_ret is not None) and (latest_frame is not None):
        image = latest_frame.copy()
    else:
        time.sleep(0.01)
        continue

    frameWidth = image.shape[1]
    frameHeight = image.shape[0]
    print(frameWidth, frameHeight)

    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

    # Fix the input Height and get the width according to the Aspect Ratio
    inHeight = 100
    inWidth = int((inHeight/frameHeight)*frameWidth)

    # Create a resized image for processing
    image = cv2.resize(image, (int((480/frameHeight)*frameWidth), 480))
    
    inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (inWidth, inHeight),
                              (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA);
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA);
    output = net.forward()

    print("Time Taken in forward pass = {}".format(time.time() - start))

    BODY_PARTS = { "RShoulder": 2, "RWrist": 4, "LShoulder": 5 }


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
        location = ((int(x), int(y)) if conf > 0.1 else None)
        points[part] = location
        cv2.circle(image, location, 5, colors[BODY_PARTS[part]%len(colors)], -1, cv2.LINE_AA)

    cv2.imshow("Keypoints", image)
    cv2.waitKey(1)
    print("Total Time Taken in code = {}".format(time.time() - start))

