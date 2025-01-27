Core directory which contains the script for detecting gestures and converting them to analog values allowing to control devices.

## Getting started
1- Install all the dependencies in requirements.txt. Make sure you compile OpenCV with CUDA DNN module.  
2- Download OpenPose body model and the `prototxt` file using the [OpenPose repo](https://github.com/CMU-Perceptual-Computing-Lab/openpose/tree/master/models) and the scripts included which help download models. To download the models used in this repo directly, use these links for [`prototxt`](https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/master/models/pose/body_25/pose_deploy.prototxt) and [`model`](http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/body_25/pose_iter_584000.caffemodel).  
3- Review `config.py` to update the configuration to suit your needs. Create `secrets.py` to keep the relevant secret configuration   
4- Run using `python gesture_rec_openpose.py`