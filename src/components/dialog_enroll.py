import streamlit as st
from src.database.config import supabase
from src.database.db import create_enrollment_request, enroll_student_to_subject
import time

@st.dialog("Enroll in a subject", width=400)
def enroll_dialog():
    st.write("Enter the subject code to enroll in a subject.")
    join_code = st.text_input("Subject Code", placeholder="e.g CS101")

    if 'enroll_selected_subject' not in st.session_state:
        st.session_state.enroll_selected_subject = None

    if join_code:
        # Fetch ALL sections for this subject code
        res = supabase.table("subjects").select("*").eq("subject_code", join_code).execute()

        if res.data:
            student_id = st.session_state.student_data["student_id"]

            # Check which sections student is already enrolled in
            already_enrolled_ids = set()
            for subj in res.data:
                check = supabase.table("subject_students")\
                    .select("*")\
                    .eq("subject_id", subj["subject_id"])\
                    .eq("student_id", student_id).execute()
                if check.data:
                    already_enrolled_ids.add(subj["subject_id"])

            # Build section options — exclude already enrolled ones
            available = [s for s in res.data if s["subject_id"] not in already_enrolled_ids]

            if not available and already_enrolled_ids:
                st.warning("You are already enrolled in all sections of this subject.")
            elif not available:
                st.error("No sections available for this subject code.")
            else:
                # Check if student is already in ANY section of this subject
                if already_enrolled_ids:
                    st.warning("⚠️ You are already enrolled in a section of this subject. Enrolling in another section is not allowed.")
                else:
                    # NEW — with this
                    section_options = {f"Section {s['section']} — {s['name']}": s for s in available}
                    all_options = ["— Select a section —"] + list(section_options.keys())
                    selected_label = st.selectbox("Select Section", options=all_options)

                    if selected_label != "— Select a section —":
                        st.session_state.enroll_selected_subject = section_options[selected_label]
                    else:
                        st.session_state.enroll_selected_subject = None



        elif join_code:
            st.error("Invalid subject code. Please try again.")

    if st.button("Enroll Now", type="primary", width='stretch'):
        if not join_code:
            st.error("Please enter a subject code.")
        elif st.session_state.enroll_selected_subject:
            student_id = st.session_state.student_data["student_id"]

            selected_subject = st.session_state.enroll_selected_subject

            request_sent = create_enrollment_request(
                student_id,
                selected_subject["subject_id"],
                selected_subject["teacher_id"]
            )

            if request_sent:
                st.success(
                    f"Enrollment request sent for {selected_subject['name']} — Section {selected_subject['section']}!"
                )

                st.session_state.enroll_selected_subject = None

                time.sleep(2)
                st.rerun()

            else:
                st.warning("Enrollment request already sent!")
        else:
            st.error("Please select a section first.")