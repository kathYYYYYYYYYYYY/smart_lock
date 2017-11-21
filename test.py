from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import sched
from datetime import datetime, date

import face_recognition
import cv2
import FacialRecognitionManager
import LockManager
import time

lockManager = LockManager.LockManager()
facialRecognitionManager = FacialRecognitionManager.FacialRecognitionManager()


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 10
# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0



# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
all_faces = facialRecognitionManager.getUserImages()
user_face_encodings = {}

for user in all_faces:
    faces = all_faces[user]
    for face in faces:
        image = face_recognition.load_image_file(face)
        # the higher the accurate
        encoding = face_recognition.face_encodings(image, num_jitters=200)
        if len(encoding) >= 1:
            if user in user_face_encodings:
                user_face_encodings[user].append(encoding[0])
            else:
                user_face_encodings[user] = [encoding[0]]

#print(user_face_encodings)
#obama_image = face_recognition.load_image_file("1.jpg")
#obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

UNBLOCK_TIME = 0
UNLOCK_CD = 50
UNKNOW_NAME = 'Unknown'

confident = 0
matching_confident = 8

confident_stranger = 0
matching_confident_stranger = 10

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            faces = []
            names = []
            for user_name in user_face_encodings:
                for face in user_face_encodings[user_name]:
                    faces.append(face)
                    names.append(user_name)

            match = face_recognition.compare_faces(faces, face_encoding, tolerance=0.45)
            #print(match)
            #print(names)
            name = UNKNOW_NAME
            for i in range(len(match)):
                if match[i]:
                    name = names[i]
                    #print("Found matched face", name)
                    face_names.append(name)
                else:
                    face_names.append("Unknown")
        # Got host faces
        if len(face_names) != face_names.count(UNKNOW_NAME) and int(time.time()) > UNBLOCK_TIME:
            print(confident)
            # START of blink detections
            frame = imutils.resize(frame, width=250)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect faces in the grayscale frame
            rects = detector(gray, 0)
            # loop over the face detections
            for rect in rects:
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                # extract the left and right eye coordinates, then use the
                # coordinates to compute the eye aspect ratio for both eyes
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)

                # average the eye aspect ratio together for both eyes
                ear = (leftEAR + rightEAR) / 2.0

                if ear < EYE_AR_THRESH:
                    confident += 1
                    break
                else:
                    # reset the eye frame counter
                    confident = 0

            # END of blink detections
            if confident >= matching_confident:
                print("Host detected, trying to unlock...")
                result = lockManager.doUnlock(name)
                if result:
                    print('Unlocked door, stop scanning for ' + str(UNLOCK_CD) + 'sec')
                    UNBLOCK_TIME = int(time.time()) + UNLOCK_CD
                else:
                    print('Failed to unlock, wait for 20 secs')
                    UNBLOCK_TIME = int(time.time()) + 20
                confident = 0
        elif len(face_names) != 0 and len(face_names) == face_names.count(UNKNOW_NAME) and int(time.time()) > UNBLOCK_TIME:
            confident_stranger += 1
            confident -= 1
            print(confident_stranger)
            if confident_stranger >= matching_confident_stranger:
                print("Unknown face detected, trying to inform host...")
                lockManager.askHostPermission()
                print('Informed host, stop scanning for ' + str(UNLOCK_CD) + 'sec')
                UNBLOCK_TIME = int(time.time()) + UNLOCK_CD
                confident_stranger = 0

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
