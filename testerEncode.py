import face_recognition
import cv2
from dotenv import load_dotenv
import os

load_dotenv()

video_capture = cv2.VideoCapture(os.getenv("URL_RTSP"))

while True:
    ret, frame = video_capture.read()

    if ret:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        face_locations = face_recognition.face_locations(frame, model="hog")

        for top, right, bottom, left in face_locations:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.imshow('Video', small_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()