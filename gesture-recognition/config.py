## This contains all configuration for the Gesture recognition part
from secrets import password

####################### Gesture detection settings ####################################
rtsp_username = "admin"
rtsp_password = password
rtsp_url = "192.168.1.14:554"
RTSP_STREAM = "rtsp://" + rtsp_username + ":" + rtsp_password + "@" + rtsp_url 

# The height for resizing the image before processing it through OpenPose. The width
# is calculated automatically to maintain the aspect ratio.
# A smaller image will get processed faster at the cost of reduced accuracy.
IMAGE_RESIZE_HEIGHT = 720

# Input dimensions(H, W) for the OpenPose CNN.
# A smaller dimension will get processed faster but might not be accurate. 
CNN_INPUT_DIM = (368, 368)

# Location of the OpenPose model
PROTO_FILE = "body/pose_deploy.prototxt.txt"
WEIGHTS_FILE = "body/pose_iter_584000.caffemodel"

####################### Device control settings ####################################
# ESP Host to call
ENDPOINT_HOST = "http://192.168.1.10"

# The time(in sec) after which a gesture is considered stale and is discarded.
# Having a high timeout can also lead to a lag effect.
ACTION_TIMEOUT = 1

# The time(in sec) after which an HTTP request to the ESP endpoint times out.
API_REQUEST_TIMEOUT = 6

