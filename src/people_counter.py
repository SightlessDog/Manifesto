# -*- coding: utf-8 -*-
from center_tracker import center_tracker
from persontrackable import PersonTrackable
from Stitcher.stitch import stitch
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import multiprocessing
import argparse
import imutils
import time
import dlib
import cv2
import json
from Kafka.kafkaProducer import kafka_producer

def start_t(box, label, rgb, inputQueue, outputQueue):
    # construct a dlib rectangle object from the bounding box
    # coordinates and then start the correlation tracker
    t = dlib.correlation_tracker()
    rect = dlib.rectangle(box[0], box[1], box[2], box[3])
    t.start_track(rgb, rect)
    trackers.append(t)

    while True:
        rgb = inputQueue.get()

        if rgb is not None:
            t.update(rgb)
            pos = t.get_position()

            # unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            # add the label + bounding box coordinates to the output
            # queue
            outputQueue.put((label, (startX, startY, endX, endY)))

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt",
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model",
                help="path to Caffe pre-trained model")
ap.add_argument("-i1", "--firstInput", type=str,
                help="path to optional input video file")
ap.add_argument("-i2", "--secondInput", type=str,
                help="path to optional second input video file")
ap.add_argument("-o", "--output", type=str,
                help="path to optional output video file")
ap.add_argument("-c", "--confidence", type=float, default=0.4,
                help="minimum probability to filter weak detections")
ap.add_argument("-s", "--skip-frames", type=int, default=30,
                help="# of skip frames between detections")
args = vars(ap.parse_args())

# initialize our lists of queues -- both input queue and output queue
# for *every* object that we will be tracking
inputQueues = []
outputQueues = []

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

print("[INFO] loading models...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

if not args.get("input", False):
    print("[INFO] starting cameras...")
    vs1 = VideoStream(src=0).start()
    vs2 = VideoStream(src=1).start()
    time.sleep(2.0)
writer = None
# Frame dimensions initialisation
W = None
H = None
# center_tracker initialisation, list to store the dlib correlation trackers and dict to map each object_id to a persontrackable
ct = center_tracker(max_disappeared=40)
trackers = []
trackable_persons = {}
# Frames initialisation, and moving persons
total_frames = 0
total_persons = 0
stitch = stitch()
producer = kafka_producer(1002, "raspi1")

fps = FPS().start()

while True:
    #frame1 = vs1.read()
    frame2 = vs2.read()

    # frame = stitch.update(frame1, frame2)
    # resize the frame and convert it from bgr to rgb for dlib
    frame = imutils.resize(frame2, width=400)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Set the frame dimensions
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    # The current status and list of the bounding box rectangles
    status = "Waiting"
    rects = []
    # Trigger object detection each x frames
    if total_frames % args["skip_frames"] == 0 and len(inputQueues) == 0:
        status = "Detecting"
        trackers = []
        # Convert the frame to a blob
        blob = cv2.dnn.blobFromImage(rgb, 0.008, (W, H), 127, 5)
        net.setInput(blob)
        detections = net.forward()
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            # Filter out weak detections by requiring a minimum confidence
            if confidence > args["confidence"]:
                # Extract the index from the list
                idx = int(detections[0, 0, i, 1])
                label = CLASSES[idx]
                # if the class label is not a person, ignore it
                if CLASSES[idx] != "person":
                    continue
                # compute the (x, y)-coordinates of the bounding box for the object
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")
                # Construct a dlib rectangle object from the bounding box coords and then start the dlib correlatio tracker
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(startX, startY, endX, endY)
                tracker.start_track(rgb, rect)
                # Add the tracker to the list of trackers so we can utilize them when skipping the frames
                trackers.append(tracker)
    # Otherwise we use our trackers list
    else:
        for tracker in trackers:
            status = "Tracking"
            # Update the tracker and grab the updated position
            tracker.update(rgb)
            pos = tracker.get_position()
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            rects.append((startX, startY, endX, endY))

        objects = ct.update(rects)

        for (object_id, center) in objects.items():
            to = trackable_persons.get(object_id, None)
            if to is None:
                to = PersonTrackable(object_id, center)
            else:
                to.centers.append(center)
                if not to.counted:
                    to.counted = True

            trackable_persons[object_id] = to
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(object_id)
            cv2.putText(frame, text, (center[0] - 10, center[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (center[0], center[1]), 4, (0, 255, 0), -1)
            x_center = int(center[0])
            y_center = int(center[1])
            # print(center[0], x_center)
            # print(center[1], y_center)
            print(x_center, y_center)
            data_to_send = {"centerX": int(x_center), "centerY": int(y_center), "id": int(object_id)}
            json_data = json.dumps(data_to_send)
            producer.send(data_to_send)
    info = [
        ("Status", status),
    ]
    # loop over the info tuples and draw them on our frame
    for (i, (k, v)) in enumerate(info):
        text = "{}: {}".format(k, v)
        cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    # increment the total number of frames processed thus far and
    # then update the FPS counter
    total_frames += 1
    fps.update()

# stop the timer and display FPS information
fps.stop()
# print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
vs2.release()
cv2.destroyAllWindows()