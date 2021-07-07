# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import pdb
from gpiozero import Servo
import time
import math
import pathlib
from threading import Thread
import importlib.util
import datetime
from videostream import VideoStream
from jumpingjackcounter import JumpingJackCounter
from subprocess import call
from pygame import mixer
import vlc

import time
import RPi.GPIO as GPIO

MODEL_NAME = "posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite"#args.modeldir
OUTPUT_PATH = "pose_images"
GRAPH_NAME = "detect.tflite"
LABELMAP_NAME = "labelmap.txt"
min_conf_threshold = float(0.4)
# resW, resH = args.resolution.split('x')
imW, imH = 1280, 720 #int(resW), int(resH)
use_TPU = False
debug = True
instructor_audio = [
    "whistle_alarm"
    "intro",
    "too slow",
    "successful"
]

pose_definitions = {
    "nose": 0,
    "leftEye": 1,
    "rightEye": 2,
    "leftEar": 3,
    "rightEar": 4,
    "leftShoulder": 5,
    "rightShoulder": 6,
    "leftElbow": 7,
    "rightElbow": 8,
    "leftWrist": 9,
    "rightWrist": 10,
    "leftHip": 11,
    "rightHip": 12,
    "leftKnee": 13,
    "rightKnee": 14,
    "leftAnkle": 15,
    "rightAnkle": 16
}



input_template = pose_definitions.copy()

for key in input_template.keys():
    input_template[key] = (-1,-1)


# Import TensorFlow libraries
# If tensorflow is not installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tensorflow')
if pkg is None:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter
    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME = 'edgetpu.tflite'       

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME)


# If using Edge TPU, use special load_delegate argument
if use_TPU:
    interpreter = Interpreter(model_path=PATH_TO_CKPT,
                              experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print(PATH_TO_CKPT)
else:
    interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

#set stride to 32 based on model size
output_size = 32
output_stride = 8

floating_model = ----(input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5


def mod(a, b):
    """find a % b"""
    floored = np.floor_divide(a, b)
    return np.subtract(a, np.multiply(floored, b))

def sigmoid(x):
    """apply sigmoid actiation to numpy array"""
    return 1/ (1 + np.exp(-x))
    
def sigmoid_and_argmax2d(inputs, threshold):
    """return y,x coordinates from heatmap"""
    #v1 is 9x9x17 heatmap
    v1 = interpreter.get_tensor(output_details[0]['index'])[0]
    height = v1.shape[0]
    width = v1.shape[1]
    depth = v1.shape[2]
    reshaped = np.reshape(v1, [height * width, depth])
    reshaped = sigmoid(reshaped)
    #apply threshold
    reshaped = (reshaped > threshold) * reshaped
    coords = np.argmax(reshaped, axis=0)
    yCoords = np.round(np.expand_dims(np.divide(coords, width), 1)) 
    xCoords = np.expand_dims(mod(coords, width), 1) 
    return np.concatenate([yCoords, xCoords], 1)

def get_offset_point(y, x, offsets, keypoint, num_key_points):
    """get offset vector from coordinate"""
    y_off = offsets[y,x, keypoint]
    x_off = offsets[y,x, keypoint+num_key_points]
    return np.array([y_off, x_off])
    

def get_offsets(output_details, coords, num_key_points=17):
    """get offset vectors from all coordinates"""
    offsets = interpreter.get_tensor(output_details[1]['index'])[0]
    offset_vectors = np.array([]).reshape(-1,2)
    for i in range(len(coords)):
        heatmap_y = int(coords[i][0])
        heatmap_x = int(coords[i][1])
        #make sure indices aren't out of range
        if heatmap_y >8:
            heatmap_y = heatmap_y -1
        if heatmap_x > 8:
            heatmap_x = heatmap_x -1
        offset_vectors = np.vstack((offset_vectors, get_offset_point(heatmap_y, heatmap_x, offsets, i, num_key_points)))  
    return offset_vectors

def draw_lines(keypoints, image, bad_pts):
    """connect important body part keypoints with lines"""
    #color = (255, 0, 0)
    color = (0, 255, 0)
    thickness = 2
    #refernce for keypoint indexing: https://www.tensorflow.org/lite/models/pose_estimation/overview
    body_map = [[5,6], [5,7], [7,9], [5,11], [6,8], [8,10], [6,12], [11,12], [11,13], [13,15], [12,14], [14,16]]
    for map_pair in body_map:
        #print(f'Map pair {map_pair}')
        if map_pair[0] in bad_pts or map_pair[1] in bad_pts:
            continue
        start_pos = (int(keypoints[map_pair[0]][1]), int(keypoints[map_pair[0]][0]))
        end_pos = (int(keypoints[map_pair[1]][1]), int(keypoints[map_pair[1]][0]))
        image = cv2.line(image, start_pos, end_pos, color, thickness)
    return image

       
def speakStatus(text):
    call(["espeak","-s140 -ven+18 -z",text])

def playTrack(file):       
#     mixer.init()
#     mixer.music.load(file)
#     mixer.music.play()
    player = vlc.MediaPlayer(file)
    player.play()
    


def processImage():
    print('running loop')
    t1 = cv2.getTickCount()
        
    # Grab frame from video stream
    frame1 = vs.read()
    
    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)
    frame_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()
    
    #get y,x positions from heatmap
    coords = sigmoid_and_argmax2d(output_details, min_conf_threshold)
#         print(coords)
    #keep track of keypoints that don't meet threshold
    drop_pts = list(np.unique(np.where(coords ==0)[0]))
    #get offets from postions
    offset_vectors = get_offsets(output_details, coords)
    #use stride to get coordinates in image coordinates
    keypoint_positions = coords * output_size + offset_vectors
#         print(keypoint_positions)
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    input_coords = input_template.copy()

    for i in range(len(keypoint_positions)):
        #don't draw low confidence points
        # Center coordinates
        if i in drop_pts:
            continue
        
        x = int(keypoint_positions[i][1])
        y = int(keypoint_positions[i][0])
        center_coordinates = (x, y)
        
        input_coords[list(input_template.keys())[i]] = center_coordinates
        
        if debug:
            radius = 2
            color = (0, 255, 0)
            thickness = 2
            cv2.circle(frame_resized, center_coordinates, radius, color, thickness)
            cv2.putText(frame_resized, str(i), (x-4, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1) # Draw label text

    
    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1
    fps_string = 'FPS: {0:.2f}'.format(frame_rate_calc)

    #save image with time stamp to directory
    if debug:
        frame_resized = draw_lines(keypoint_positions, frame_resized, drop_pts)
        cv2.putText(frame_resized,fps_string,(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        f.append(frame_rate_calc)
        path = str(outdir) + '/'  + str(datetime.datetime.now()) + ".jpg"
        status = cv2.imwrite(path, frame_resized)

    return input_coords

def startSequence():
    pass

def tooSlowSequence():
    servo.value = -1
    time.sleep(0.5)
    servo.detach()
    Thread(playTrack("audio/tooslow.mp3")).start()
    servo.value = 1
    time.sleep(0.5)
    servo.detach()
    
def finishSequence():
    servo.value = -1
    time.sleep(0.5)
    servo.detach()
    Thread(playTrack("audio/dismissed.mp3")).start()
    time.sleep(2)
    servo.value = 1
    time.sleep(0.5)
    servo.detach()
    time.sleep(2)
    


def stopStream():
    cv2.destroyAllWindows()
    vs.stop()
    print('Stopped video stream.')


try:
    servo = Servo(17)
    servo.value = 1
    servo.detach()
        
    while True:
        time.sleep(1)
        if debug:
            outdir = pathlib.Path(OUTPUT_PATH) / time.strftime('%Y-%m-%d_%H-%M-%S-%Z')
            outdir.mkdir(parents=True)
    #     GPIO.output(4, True)
        f = []
        # Initialize frame rate calculation
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()
        print(f"Freq: {freq}")
        vs = VideoStream(resolution=(imW,imH),framerate=30).start()
        time.sleep(1)
        jjc = JumpingJackCounter()
        
        userReady = False
        #for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        
        
        loop_ready_count = 0
        while not userReady:
            input_coords = processImage()
            if loop_ready_count % 2 == 0:
                playTrack("audio/air horn.mp3")
            else:
                playTrack("audio/announcement.mp3")
            time.sleep(3)
            loop_ready_count += 1
            userReady =  jjc.isReady(input_coords)
        
        time.sleep(0.1)
        Thread(playTrack(f"audio/alright_go.mp3")).start()
        
        
        while jjc.getCount() < 10:
            input_coords = processImage() 
            boolCounterIncreased = jjc.processCoords(input_coords)
            if boolCounterIncreased:
                if jjc.getCount() == 1:
                    Thread(playTrack("audio/confirmation_1.mp3")).start()
                elif jjc.getCount() % 5 == 0:
                    Thread(playTrack(f"audio/confirmation_{jjc.getCount()}.mp3")).start()
            elif jjc.secondsSinceLastRep() > 5:
                Thread(tooSlowSequence()).start()
            
            # Start timer (for calculating frame rate)
        
        time.sleep(2)
        finishSequence()
        vs.stop()
        
    
    
except KeyboardInterrupt:
    # Clean up
    stopStream()
#     GPIO.output(4, False)
#     GPIO.cleanup()
    #print(str(sum(f)/len(f)))
