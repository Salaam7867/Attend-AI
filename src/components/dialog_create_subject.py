import streamlit as st
from src.database.db import create_subject, subject_code_exists

@st.dialog("create_subject_dialog", width=400)
def dialog_create_subject(teacher_id):
        
        st.subheader("Create New Subject")
        #st.write("Fill in the details below to create a new subject.")
        subject_name = st.text_input("Subject Name", placeholder="Enter subject name", max_chars=50)
        subject_code = st.text_input("Subject Code", placeholder="Enter unique subject code", max_chars=20)
        section = st.selectbox("Section", options=["A", "B", "C", "D"], index=0)
        submit_btn = st.button("Create Subject")

        if submit_btn:
            if not subject_name or not subject_code or not section:
                st.error("Please fill in all fields.")
            elif subject_code_exists(subject_code,section):
                st.error("Subject code already exists. Please choose a different code.")
            
            else:
                result = create_subject(subject_name, subject_code, section, teacher_id)
                if result:
                    st.success(f"Subject '{subject_name}' created successfully!")
                else:
                    st.error("Failed to create subject. Please try again.")


