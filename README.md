The next thing for home automation, use gestures to control analog settings around you: Control volume, fan speed, temperature, light brightness using gestures. Exploring how simple and intuitive gestures can replace the limitations of controlling analog settings using physical knobs. 

## Demo
Working for controlling the volume on my Vankyo V600 projector. The detection works well even in the dark with my Amcrest security camera. 

![Light Mode](https://github.com/kunalgrover05/analog-gesture-control-alexa/blob/master/Gestures_for_Home_automation_Analog_control_Light_mode.gif)
![Dark Mode](https://github.com/kunalgrover05/analog-gesture-control-alexa/blob/master/Gestures_for_Home_automation_Analog_control_Dark_mode.gif)

## How does it work?
Uses OpenPose under the hood for realtime pose detection. Complete writeup of how this works can be found in my blog: [Revolutionizing Home automation: Gesture control for analog settings](https://crondev.blog/2020/09/24/gesture-control-analog-settings-volume/)

![Overall design](https://github.com/kunalgrover05/analog-gesture-control-alexa/blob/master/GestureControl.png)

## Folder structure
### Projector control
Directory containing ESP8266 code. ESP8266 rnus a HTTP server and handles commands sent to control the volume using Arduino IRSend library.

### alexa-handler
Flask server for handling requests coming using Alexa custom skill endpoint. Proxied using NGrok. 

## How to setup
TODO
