import streamlit as st
from src.database.config import supabase
from src.database.db import get_pending_requests, approve_enrollment_request, reject_enrollment_request

@st.dialog("Enrollment Requests")
def enrollment_requests_dialog(subject):

    pending_requests = get_pending_requests(subject['subject_id'])

    if not pending_requests:
        st.info("No pending requests.")
        return

    for req in pending_requests:

        student_name = req['students']['name']

        c1, c2, c3 = st.columns([3,1,1])

        with c1:
            st.write(student_name)

        with c2:
            if st.button("Approve", key=f"approve_{req['id']}"):

                approve_enrollment_request(
                    req['id'],
                    req['student_id'],
                    req['subject_id']
                )

                st.success("Approved!")
                st.rerun()

        with c3:
            if st.button("Reject", key=f"reject_{req['id']}"):

                reject_enrollment_request(req['id'])

                st.warning("Rejected!")
                st.rerun()