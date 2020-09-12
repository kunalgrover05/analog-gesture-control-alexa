
import cv2
import time
import numpy as np
import threading
from threading import Lock
#vcap = cv2.VideoCapture("rtsp://admin:test1234@192.168.1.6:554")
vcap = cv2.VideoCapture(0)
cv2.namedWindow('VIDEO', cv2.WINDOW_NORMAL)
cv2.resizeWindow('VIDEO', 600, 600)
protoFile = "hand/pose_deploy.prototxt"
weightsFile = "hand/pose_iter_102000.caffemodel"
nPoints = 22
POSE_PAIRS = [ [0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],[0,17],[17,18],[18,19],[19,20] ]

latest_frame = None
last_ret = None
lo = Lock()
import csv
import datetime


import pandas as pd

data = pd.read_csv('Current.csv', header=None)


# In[10]:


import numpy as np

data_arc_tan = data.iloc[:, 0:20]

data_arc_tan = np.arctan(data_arc_tan)


# In[19]:


from sklearn.linear_model import LinearRegression

model = LinearRegression()
y = data[21]
model.fit(data_arc_tan, y)
def rtsp_cam_buffer(vcap):
    global latest_frame, lo, last_ret

    while True:
        with lo:
            last_ret, latest_frame = vcap.read()


t1 = threading.Thread(target=rtsp_cam_buffer,args=(vcap,),name="rtsp_read_thread")
t1.daemon=True
t1.start()

with open(str(datetime.datetime.now()), 'w', newline='') as file:
    writer = csv.writer(file)
    while(1):
        if (last_ret is not None) and (latest_frame is not None):
            frame = latest_frame.copy()
        else:
            time.sleep(0.1)
            continue
        frame = cv2.resize(frame, (500,500))
        frameCopy = np.copy(frame)
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
        threshold = 0

        net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA);
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA);

        t = time.time()
        # input image dimensions for the network
        inWidth = 368
        inHeight = 368
        inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                (0, 0, 0), swapRB=False, crop=False)

        net.setInput(inpBlob)

        output = net.forward()
        print("time taken by network : {:.3f}".format(time.time() - t))

        H = output.shape[2]
        W = output.shape[3]

        # Empty list to store the detected keypoints
        points = []

        for i in range(nPoints):
            # confidence map of corresponding body's part.
            probMap = output[0, i, :, :]

            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
            
            # Scale the point to fit on the original image
            x = (frameWidth * point[0]) / W
            y = (frameHeight * point[1]) / H

            if prob > threshold : 
                cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

                # Add the point to the list if the probability is greater than the threshold
                points.append((int(x), int(y)))
            else :
                points.append(None)
        
        s = 0

        all_angles = []
        # Draw Skeleton
        for pair in POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]

            if points[partA] and points[partB]:
                cv2.line(frame, points[partA], points[partB], (0, 255, 255), 2)
                cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                try:
                    all_angles.append((points[partB][1]-points[partA][1]) / (points[partB][0] - points[partA][0]))
                except ZeroDivisionError:
                    all_angles.append(np.inf)

        # Use all angles directly
        y_pred = model.predict(np.arctan(all_angles).reshape(1, 20))
        print("Predicted angle", y_pred)
        writer.writerow(all_angles)

        # Using these points to determine the orientation of the hand till the hand gets closed
        # Only relative start and stop angles matter for the entire hand center
        try:
            finger1 = (points[1][1] - points[0][1]) / (points[1][0] - points[0][0])
            finger2 = (points[5][1] - points[0][1]) / (points[5][0] - points[0][0])
            finger3 = (points[9][1] - points[0][1]) / (points[9][0] - points[0][0])
            finger4 = (points[13][1] - points[0][1]) / (points[13][0] - points[0][0])
            finger5 = (points[17][1] - points[0][1]) / (points[17][0] - points[0][0])
#            print("Finger1", finger1)
#            print("Finger2", finger2)
#            print("Finger3", finger3)
#            print("Finger4", finger4)
#            print("Finger5", finger5)
#
        except Exception as e:
            print(e)
            pass
        cv2.imshow('Output-Keypoints', frameCopy)
        cv2.imshow('Output-Skeleton', frame)

        print("Total time taken : {:.3f}".format(time.time() - t))

        cv2.waitKey(1)


