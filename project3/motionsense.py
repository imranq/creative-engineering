import os
import datetime as dt
from gpiozero import MotionSensor
from picamera import PiCamera
from signal import pause

destination = '/home/pi/video'
camera = PiCamera()
sensor = MotionSensor(4)

def record_video():
    filename = os.path.join(destination, dt.datetime.now().strftime('%Y-%m-%d_%H.%M.%S.h264'))
    camera.start_preview()
    camera.start_recording(filename)

def finish_video():
    camera.stop_recording()
    camera.stop_preview()

sensor.when_motion = record_video
sensor.when_no_motion = finish_video
pause()