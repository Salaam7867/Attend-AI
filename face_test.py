import face_recognition
import cv2

# load known image
known_image = face_recognition.load_image_file("student.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    rgb = frame[:, :, ::-1]

    faces = face_recognition.face_encodings(rgb)

    for face in faces:
        match = face_recognition.compare_faces([known_encoding], face)

        if True in match:
            print("MATCH FOUND")

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()