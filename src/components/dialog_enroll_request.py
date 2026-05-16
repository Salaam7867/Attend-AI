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

        c1, c2, c3 = st.columns([4, 1.3, 1.3])

        with c1:
            st.markdown(
                f"""
                <div style="
                    padding-top:12px;
                    font-weight:600;
                    word-break:break-word;
                ">
                    {student_name}
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            if st.button(
                "Approve",
                key=f"approve_{req['id']}",
                type="primary",
                use_container_width=True
            ):
                approve_enrollment_request(
                    req['id'],
                    req['student_id'],
                    req['subject_id']
                )

                st.success("Approved!")
                st.rerun()

        with c3:
            if st.button(
                "Reject",
                key=f"reject_{req['id']}",
                use_container_width=True
            ):
                reject_enrollment_request(req['id'])

                st.warning("Rejected!")
                st.rerun()

        st.divider()