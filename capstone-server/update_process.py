from enum import Enum
from data.fridge_repository import readFridge, updateFridge
from data.mutex import lock
import datetime
import os.path
import os
import json
from threading import Event, Thread, currentThread
import sys
import RPi.GPIO as GPIO
import traceback
from pathlib import Path
from leds import turnOnLight, turnOffLight, loading_update_process_lights, unregistered_lights, odl_ready_lights, odl_error_lights
from rpi_ws281x import Color, PixelStrip, ws
import time
import depthai as dai
import cv2
from multiprocessing import Queue, Process, Manager
from signal import signal, SIGINT
import base64

labels = ['Apple', 'Orange', 'Strawberry', 'Tomato']

# Hardware setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

print("running update_process script", flush=True)
print("waiting for user.json to exist", flush=True)
while not os.path.exists('user.json'):
    print("does not exist", flush=True)
    unregistered_lights()
    time.sleep(5)

turnOffLight()

def run_odl_ready_lights():
    odl_ready_lights()
    time.sleep(2)
    turnOffLight()

def loading_model_lights(arg):
    t = currentThread()
    # Show yellow lights
    while getattr(t, "is_done", True): 
        loading_update_process_lights() 

    # Show sucecssfully loaded model lights (green)
    run_odl_ready_lights()
    turnOffLight()

update_process_lights_thread = Thread(target=loading_model_lights, args=("is_done",))
update_process_lights_thread.start()

print("found user.json")
dir = os.path.dirname(__file__)
fname = os.path.join(dir, 'user.json')
sensor_delay = 1

# Setup the ODL device
model_path2 = "4ingraugmented_openvino_2022.1_6shave.blob"
config_path2 = "4ingraugmented.json"
model_path = "yolov7appleorangestrawberrytomato_openvino_2021.4_6shave.blob"
config_path = "yolov7appleorangestrawberrytomato.json"

configPath = Path(config_path2)
if not configPath.exists():
    raise ValueError("Path {} does not exist!".format(configPath))

with configPath.open() as f:
    config = json.load(f)
    
nnConfig = config.get("nn_config", {})

# extract metadata
metadata = nnConfig.get("NN_specific_metadata", {})
classes = metadata.get("classes", {})
coordinates = metadata.get("coordinates", {})
anchors = metadata.get("anchors", {})
anchorMasks = metadata.get("anchor_masks", {})
iouThreshold = metadata.get("iou_threshold", {})
confidenceThreshold = metadata.get("confidence_threshold", {})

print(metadata, flush=True)

# parse labels
nnMappings = config.get("mappings", {})
#labels = nnMappings.get("labels", {})

# get model path
if not Path(model_path2).exists():
    print("No blob found at {}. Looking into DepthAI model zoo.".format(model_path2), flush=True)
    raise ValueError("Model Path {} does not exist!".format(model_path2))
    #model_path = str(blobconverter.from_zoo(model_path, shaves = 6, zoo_type = "depthai", use_cache=True))
else:
    print("model found", flush=True)
# sync outputs
syncNN = True

# Create pipeline
pipeline = dai.Pipeline()

print("initialized pipeline", flush=True)
# Create ImageManip node
manip = pipeline.create(dai.node.ImageManip)
manip.initialConfig.setResize(640, 640)
manip.initialConfig.setFrameType(dai.ImgFrame.Type.BGR888p)
manip.setMaxOutputFrameSize(640*640*3)

print("created manip node", flush=True)

# Create input control node to acquire capture command
xinCaptureCommand = pipeline.create(dai.node.XLinkIn)
xinCaptureCommand.setStreamName("capture")

# Create Camera node and give its properties
camRGB = pipeline.create(dai.node.ColorCamera)
camRGB.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
camRGB.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
camRGB.setPreviewSize(2, 2)
camRGB.setFp16(True)

print("created camRGB node", flush=True)

detectionNetwork = pipeline.create(dai.node.YoloDetectionNetwork)

print("pipeline created detection network", flush=True)
# Create output node for neural network
nnOut = pipeline.create(dai.node.XLinkOut)
nnOut.setStreamName("nn")

print("created nnOut output node", flush=True)

# Create output node for still images
outStillRGB = pipeline.create(dai.node.XLinkOut)
outStillRGB.setStreamName("rgbStill")

print("created outStillRGB node for still images", flush=True)

# Network specific settings
detectionNetwork.setConfidenceThreshold(confidenceThreshold)
print("1", flush=True)
detectionNetwork.setNumClasses(classes)
print("2", flush=True)
detectionNetwork.setCoordinateSize(coordinates)
print("3", flush=True)
detectionNetwork.setAnchors(anchors)
print("4", flush=True)
detectionNetwork.setAnchorMasks(anchorMasks)
print("5", flush=True)
detectionNetwork.setIouThreshold(iouThreshold)
print(f"6: {model_path}", flush=True) 
detectionNetwork.input.setBlocking(False)
print("7", flush=True)
detectionNetwork.setBlobPath(model_path)
print("8", flush=True)
detectionNetwork.setNumInferenceThreads(2)
print("9", flush=True)


print("created detection network", flush=True)

# Linking

# Link output of xinCaptureCommand to camera input control
xinCaptureCommand.out.link(camRGB.inputControl)

camRGB.still.link(manip.inputImage)
manip.out.link(detectionNetwork.input)

# Link output of detectionNetwork to camera input
detectionNetwork.passthrough.link(outStillRGB.input)

# Link output of detectionNetwork to NN input
detectionNetwork.out.link(nnOut.input)

print("created nodes successfully", flush=True)
try:
    device = dai.Device(pipeline)
    #device.setLogLevel(dai.LogLevel.DEBUG)
    #device.setLogOutputLevel(dai.LogLevel.DEBUG)
    print(f"Found device {device}", flush=True) 
    print(device.getUsbSpeed()) 
except:
    # Show error for odl lights
    odl_error_lights()
    exit()

# Create input queue to device, that receives capture command
captureInputQueue = device.getInputQueue("capture")

# Create output queue that will get RGB frame (Output from device, and input to host)
stillQueue = device.getOutputQueue(name="rgbStill")

# Create output queue that will get detections (Output from NN ?)
detectionQueue = device.getOutputQueue(name="nn")
print("initialized queues", flush=True)

# Close update process lights thread (stop yellow lights)
update_process_lights_thread.is_done = False

# We define states using booleans to determine whether or not the Fridge is open
class FridgeDoorState(Enum):
    OPEN = 1
    CLOSED = 2

def get_state(previous_fridge_state):
    # Based on Sensor light threshold data, return open or closed, remove parameter when implemented
    # Alternate case for testing    
    # Light is detected
    # TODO: This needs to be updated to FridgeDoorState.CLOSED iff timer > 1 minute
    #         Reset -> timer if light is detected
    if(GPIO.input(4) == 1):
        return FridgeDoorState.CLOSED
    return FridgeDoorState.OPEN

def update_fridge_data(objects, image):
    """
    print("image:")
    print(image)
    """
    # Get the new items and update that in tracking
    #with lock:
    with open(fname, 'r') as user_credential_file:
        user_credentials = json.load(user_credential_file)
        fridge = readFridge(user_credentials['user_id'],user_credentials['fridge_id'])
        fridge["last_updated"] = datetime.datetime.now()
        fridge['items'] = objects
        # The [2:-1] takes away the ' character from first and last index
        fridge['image'] = str(image)[2:-1]
        user_credential_file.close()
        user_credentials['fridge_id']
        updateFridge(user_credentials['user_id'],user_credentials['fridge_id'], fridge)

def consume_frames(captureInputQueue, stillQueue, detectionQueue):
    print("Process is now tracking the fridge door.", flush=True)
    previous_fridge_state = FridgeDoorState.CLOSED
    current_fridge_state = FridgeDoorState.CLOSED
    startTime = time.time()
    print("Started consume frames process", flush=True)
    while(os.path.isfile(fname)):
        current_fridge_state = get_state(previous_fridge_state)
        currTime = time.time()	
        if (previous_fridge_state == FridgeDoorState.OPEN and current_fridge_state == FridgeDoorState.CLOSED):
            startTime = time.time()
            #capture_command = still_capture_mp_queue.get()
            #if capture_command is not None:
                #print(f"received mp queue item: {capture_command}", flush=True)
            print("Door was closed. Updating Fridge.", flush=True)
            print("Attempting to object detect", flush=True)
            turnOnLight()            
            objects, image = captureFrameAndDetectObjects(captureInputQueue, stillQueue, detectionQueue)
            turnOffLight()
            #Event().wait(sensor_delay)
            
            # Update firebase fridge objects
            print("updating firebase objects")
            
            thread2 = Thread(target=update_fridge_data, args=(objects, image))
            thread2.start()
            
            thread2.join()
            print("finished updating firebase objects")
        previous_fridge_state = current_fridge_state
        #Event().wait(sensor_delay)
    
def captureFrameAndDetectObjects(captureInputQueue, stillQueue, detectionQueue):
    capturedStillFrame = False
    detectedObjects = False
    
    object_count = {'Orange': 0, 'Apple': 0, 'Strawberry': 0, 'Tomato': 0}
    jpg_as_text = ""

    ctrl = dai.CameraControl()
    ctrl.setCaptureStill(True)
    captureInputQueue.send(ctrl)
    while not capturedStillFrame and not detectedObjects:
        #print("in while loop")
        inDet = detectionQueue.tryGet()
        stillFrame = stillQueue.tryGet()
        #print(f"after tryget: stillFrame: {stillFrame}, {inDet}")
        
        if stillFrame is not None:
            print("in still frame", flush=True)
            #latencyMs = (dai.Clock.now() - stillFrame.getTimestamp()).total_seconds() * 1000
            #print('Latency: {:.2f} ms'.format(latencyMs))
            print("Captured frame: ", stillFrame.getHeight(), stillFrame.getWidth(), stillFrame.getType())
            frame = stillFrame.getCvFrame()

            # Display frame with bounding boxes (broken)
            # displayFrameWithBB("rgb", frame, detections)

            # # Show still frame
            #cv2.imshow("frame", frame)

            # # Save still frame to file
            fImageName = f"still_image.jpeg"
            cv2.imwrite(fImageName, frame)

            # Save still frame text to file
            fImageTxtName = f"still_image.txt"
            retval, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            with open(fImageTxtName, "wb") as f:
                f.write(jpg_as_text)
            #print('still image frame saved to', fImageName)
            capturedStillFrame = True
            

        if inDet is not None:
            print("Detected objects:", flush=True)
            detections = inDet.detections
            for detection in detections:
                object_count[labels[detection.label]] += 1
                print(f"Object: {labels[detection.label]}, Confidence: {detection.confidence}", flush=True)
            print(object_count, flush=True)

            # Write to file
            # fName = f"{dirName}/{int(time.time() * 1000)}.txt"
            detectedObjectsFileName = "detected_objects.txt"
            """
            with open(fName, "wb") as f:
                for k, v in object_count.items():
                    b = bytes(f"{k} {v}\n", 'utf-8')
                    f.write(b)
                print('detection data saved to', fName)
            """
            detectedObjects = True
            #latencyMs = (dai.Clock.now() - inDet.getTimestamp()).total_seconds() * 1000
            #print('Detection Latency: {:.2f} ms'.format(latencyMs))
    # Set to false in order to allow camera to detect new frame (and not repeat the old one)
    ctrl.setCaptureStill(False)

    return object_count, jpg_as_text



#still_capture_mp_queue = Queue()
#update_process = Process(target=track_fridge_door, name="update_process", args=(still_capture_mp_queue,))

if(os.path.isfile(fname)):
    print("starting update_process")
    #update_process.start()
    try:
        consume_frames(captureInputQueue, stillQueue, detectionQueue)
    except KeyboardInterrupt:
        device.close()
    #device.close()
    #print("Deviced closed.", flush=True)
    #update_process.terminate()
    #update_process.join()
    #print("update_process terminated", flush=True)
    #except KeyboardInterrupt:
     #   signal(SIGKILL, terminate_proc)
      #  pass
    
