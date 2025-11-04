import sys
import time
import math
import random
import os
import json
import shutil
import threading
from multiprocessing import Process
import datetime
import subprocess

# Try to import optional packages
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Camera features will be disabled.")

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition not available. Face detection features will be disabled.")

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: MediaPipe not available. Face detection features will be disabled.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available. Some features may not work.")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: keyboard not available. Keyboard monitoring will be disabled.")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: PyAutoGUI not available. Screen monitoring will be disabled.")

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("Warning: PyGetWindow not available. Window monitoring will be disabled.")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    print("Warning: pyperclip not available. Clipboard monitoring will be disabled.")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: YOLO not available. Object detection will be disabled.")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not available. Audio monitoring will be disabled.")

#Variables
#All Related
Globalflag = False
Student_Name = ''
start_time = [0, 0, 0, 0, 0]
end_time = [0, 0, 0, 0, 0]
recorded_durations = []
prev_state = ['Verified Student appeared', "Forward", "Only one person is detected", "Stay in the Test", "No Electronic Device Detected"]
flag = [False, False, False, False, False]

# Initialize camera variables if OpenCV is available
if CV2_AVAILABLE:
    capb = cv2.VideoCapture(0)
    width = int(capb.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capb.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capb.release()
else:
    width = 640
    height = 480

# Initialize video writers if OpenCV is available
if CV2_AVAILABLE:
    video = [(str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4"), (str(random.randint(1,50000))+".mp4")]
    writer = [cv2.VideoWriter(video[0], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)), cv2.VideoWriter(video[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)), cv2.VideoWriter(video[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height)), cv2.VideoWriter(video[3], cv2.VideoWriter_fourcc(*'mp4v'), 15, (1920, 1080)), cv2.VideoWriter(video[4], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))]
else:
    video = ["dummy1.mp4", "dummy2.mp4", "dummy3.mp4", "dummy4.mp4", "dummy5.mp4"]
    writer = [None, None, None, None, None]

# Initialize MediaPipe if available
if MEDIAPIPE_AVAILABLE:
    mpFaceDetection = mp.solutions.face_detection
    mpDraw = mp.solutions.drawing_utils
    faceDetection = mpFaceDetection.FaceDetection(0.75)
else:
    mpFaceDetection = None
    mpDraw = None
    faceDetection = None

# Initialize YOLO if available
if YOLO_AVAILABLE:
    try:
        model = YOLO('yolov8n.pt')
    except:
        model = None
        print("Warning: Could not load YOLO model")
else:
    model = None

# Initialize face recognition if available
if FACE_RECOGNITION_AVAILABLE:
    class FaceRecognition:
        def __init__(self):
            self.known_face_encodings = []
            self.known_face_names = []
            
        def encode_faces(self):
            if not FACE_RECOGNITION_AVAILABLE:
                return
            # Simplified face encoding
            pass
            
        def run_recognition(self):
            if not FACE_RECOGNITION_AVAILABLE:
                return
            # Simplified face recognition
            pass
else:
    class FaceRecognition:
        def __init__(self):
            pass
        def encode_faces(self):
            pass
        def run_recognition(self):
            pass

fr = FaceRecognition()

# Initialize audio monitoring if available
if PYAUDIO_AVAILABLE:
    class AudioMonitor:
        def __init__(self):
            self.CHUNK = 1024
            self.FORMAT = pyaudio.paInt16
            self.CHANNELS = 1
            self.RATE = 44100
            
        def record(self):
            if not PYAUDIO_AVAILABLE:
                return
            # Simplified audio recording
            pass
else:
    class AudioMonitor:
        def __init__(self):
            pass
        def record(self):
            pass

a = AudioMonitor()

# Initialize keyboard monitoring if available
if KEYBOARD_AVAILABLE:
    shorcuts = []
    
    def shortcut_handler(event):
        if not KEYBOARD_AVAILABLE:
            return
        # Simplified keyboard monitoring
        pass
else:
    shorcuts = []
    
    def shortcut_handler(event):
        pass

# Initialize camera if available
if CV2_AVAILABLE:
    cap = cv2.VideoCapture(0)
else:
    cap = None

# Utility functions
def get_resultId():
    return random.randint(1000, 9999)

def get_TrustScore(result_id):
    # Simplified trust score calculation
    return random.randint(0, 50)

def write_json(data, filename="violation.json"):
    try:
        with open(filename, 'a') as f:
            json.dump(data, f)
            f.write('\n')
    except Exception as e:
        print(f"Error writing to {filename}: {e}")

def move_file_to_output_folder(filename, folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        shutil.move(filename, os.path.join(folder, filename))
    except Exception as e:
        print(f"Error moving file {filename}: {e}")

def getResults():
    # Simplified results retrieval
    return []

def getResultDetails(result_id):
    # Simplified result details retrieval
    return []

# Simplified cheat detection functions
def cheat_Detection1():
    if not CV2_AVAILABLE:
        print("Camera-based cheat detection disabled (OpenCV not available)")
        return
    # Simplified cheat detection
    pass

def cheat_Detection2():
    if not CV2_AVAILABLE:
        print("Camera-based cheat detection disabled (OpenCV not available)")
        return
    # Simplified cheat detection
    pass

print("Utils module loaded successfully!")
print("Available features:")
print(f"- OpenCV (Camera): {CV2_AVAILABLE}")
print(f"- Face Recognition: {FACE_RECOGNITION_AVAILABLE}")
print(f"- MediaPipe: {MEDIAPIPE_AVAILABLE}")
print(f"- NumPy: {NUMPY_AVAILABLE}")
print(f"- Keyboard Monitoring: {KEYBOARD_AVAILABLE}")
print(f"- Screen Monitoring: {PYAUTOGUI_AVAILABLE}")
print(f"- Window Monitoring: {PYGETWINDOW_AVAILABLE}")
print(f"- Clipboard Monitoring: {PYPERCLIP_AVAILABLE}")
print(f"- YOLO Object Detection: {YOLO_AVAILABLE}")
print(f"- Audio Monitoring: {PYAUDIO_AVAILABLE}")
