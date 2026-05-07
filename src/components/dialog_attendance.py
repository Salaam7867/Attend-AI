import streamlit as st
from src.database.config import supabase
from src.database.db import enroll_student_to_subject
import time

@st.dialog("Capture or upload photos", width='large')
def dialog_attendance(subject_id):
    st.write("Add classroom photos to scan for attendance")

    if 'photo_mode' not in st.session_state:
        st.session_state.photo_mode = 'upload'
    if 'added_photos' not in st.session_state:
        st.session_state.added_photos = []

    c1, c2 = st.columns(2, gap='small')
    with c1:
        if st.button("Camera", type="secondary", width='stretch'):
            st.session_state.photo_mode = 'camera'
    with c2:
        if st.button("Upload photos", type="primary", width='stretch'):
            st.session_state.photo_mode = 'upload'

    if st.session_state.photo_mode == 'upload':
        uploaded = st.file_uploader("Choose image files", type=["jpg","jpeg","png"],
                                     accept_multiple_files=True, label_visibility='collapsed')
        if uploaded:
            for f in uploaded:
                if f not in st.session_state.added_photos:
                    st.session_state.added_photos.append(f)

    elif st.session_state.photo_mode == 'camera':
        photo = st.camera_input("Capture", label_visibility='collapsed')
        if photo and photo not in st.session_state.added_photos:
            st.session_state.added_photos.append(photo)

    st.divider()
    if st.button("Done", type="primary", width='stretch'):
        st.rerun()