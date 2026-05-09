import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st
from PIL import Image

from src.database.db import get_all_students

@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1) # 128 embedding

        encodings.append(np.array(face_descriptor))
    return encodings


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(set(y)) < 2:
        return None

    clf = SVC(probability=True)
    clf.fit(X, y)

    return {'clf': clf, 'X': X, 'y': y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

"""
Fallback recognizer when SVM is unavailable (less than 2 students in DB).
Instead of SVM, directly compares the given face encoding against every
stored embedding in the DB using Euclidean distance.
Returns the student_id of the closest match if within threshold, else None.
"""
def find_matching_student(encoding):
    
    student_db = get_all_students()
    best_score = float('inf')
    best_id = None

    for student in student_db:
        embedding = student.get('face_embedding')
        if not embedding:
            continue
        dist = np.linalg.norm(np.array(embedding) - encoding)
        if dist < best_score:
            best_score = dist
            best_id = student['student_id']

    if best_score <= 0.6:
        return best_id
    return None

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        # SVM unavailable — fall back to direct comparison
        for encoding in encodings:
            matched_id = find_matching_student(encoding)
            if matched_id:
                detected_student[matched_id] = True
        return detected_student, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[y_train.index(predicted_id)]

        best_match_score = np.linalg.norm(student_embedding - encoding)

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)