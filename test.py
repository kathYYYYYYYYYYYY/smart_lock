import face_recognition
import cv2
import FacialRecognitionManager
import LockManager
import time

lockManager = LockManager.LockManager()
facialRecognitionManager = FacialRecognitionManager.FacialRecognitionManager()

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
all_faces = facialRecognitionManager.getUserImages()
user_face_encodings = {}

for user in all_faces:
    faces = all_faces[user]
    for face in faces:
        image = face_recognition.load_image_file(face)
        encoding = face_recognition.face_encodings(image, num_jitters=150)
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
UNLOCK_CD = 60

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

            match = face_recognition.compare_faces(faces, face_encoding, tolerance=0.4)
            name = "Unknown"
            print(match)
            #print(names)
            for i in match:
                if match[i] and name not in face_names:
                    name = names[i]
                    #print("Found matched face", name)
                    face_names.append(name)
                    # Do unlock
                    if int(time.time()) > UNBLOCK_TIME:
                        result = lockManager.doUnlock(name)
                        if result:
                            print('Unlocked door, stop scanning for ' + str(UNLOCK_CD) + 'sec')
                            UNBLOCK_TIME = int(time.time()) + UNLOCK_CD

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
