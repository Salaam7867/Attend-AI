
import time
import streamlit as st
import numpy as np
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.pipelines.face_pipeline import predict_attendance,get_face_embeddings, get_trained_model, train_classifier  
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import get_all_students, create_student
from PIL import Image

def student_screen():


    style_background_dashboard()
    style_base_layout()


    if "student_data" in st.session_state:
        student_dashboard()
        return
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()


    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("AI is recognizing you..."):
            detected,all_ids,num_faces = predict_attendance(img)
            if num_faces == 0:
                st.error("No face detected. Please try again.")
            elif num_faces > 1:
                st.error("Multiple faces detected. Please ensure only your face is visible and try again.")
            else: # num_faces == 1
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((student for student in all_students if student['student_id'] == student_id), None)
                    
                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.success(f"Welcome, {student['name']}")
                        time.sleep(2)
                        st.rerun()
                        


                else:
                    st.info("Face not recognized. Please register with your teacher to use FaceID login.")
                    show_registration = True

        if show_registration:
            with st.container():
                st.header("Register for FaceID Login", text_alignment='center')
                new_name = st.text_input("Enter your name", placeholder="John Doe"  )

                if st.button("Register FaceID", type='primary'):
                    if not new_name:
                        st.error("Please enter your name to register.")
                    else:
                        with st.spinner("creating profile..."):
                            embedding = get_face_embeddings(img)
                            if embedding:
                               face_emb = embedding[0].tolist()  # Convert numpy array to list for storage
                               response_data = create_student(new_name, face_emb)
                               if response_data:
                                    train_classifier()
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.session_state.student_data = response_data
                                    st.success("Registration successful! Please login now.")
                            else:
                                st.error("Failed to extract face embedding. Please try again with a clearer photo.")

    
    footer_dashboard()



def student_dashboard():
    student = st.session_state.student_data
    st.header(f"Welcome, {student['name']}!", text_alignment='center')
    st.subheader("This is your student dashboard. Here you can view your attendance records and manage your profile.")
