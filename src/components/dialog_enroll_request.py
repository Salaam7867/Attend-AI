import streamlit as st
from src.database.config import supabase
from src.database.db import get_pending_requests, approve_enrollment_request, reject_enrollment_request

@st.dialog("Enrollment Requests")
def enrollment_requests_dialog(subject):

    st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 0 !important;
        flex-shrink: 1 !important;
    }
    /* Make buttons small and square */
    [data-testid="stHorizontalBlock"] .stButton button {
        padding: 4px 8px !important;
        font-size: 16px !important;
        line-height: 1 !important;
        min-height: 36px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    pending_requests = get_pending_requests(subject['subject_id'])

    if not pending_requests:
        st.info("No pending requests.")
        return

    count = len(pending_requests)
    st.caption(f"{count} pending request{'s' if count != 1 else ''}")

    if count > 1:
        if st.button(f"✓ Approve all ({count})", use_container_width=True, type="primary"):
            for req in pending_requests:
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
            st.success(f"Approved {count} students!")
            st.rerun()

    st.divider()

    for req in pending_requests:
        student_email = req['students'].get('email', '')
        student_name  = req['students'].get('name', student_email)

        # Everything on ONE line: name | ✓ | ✕
        col_name, col_approve, col_reject = st.columns([7, 1, 1])

        with col_name:
            st.write(student_name)   # native st.write — always visible in any theme

        with col_approve:
            if st.button("✓", key=f"approve_{req['id']}", type="primary",
                         help="Approve", use_container_width=True):
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
                st.rerun()

        with col_reject:
            if st.button("✕", key=f"reject_{req['id']}",
                         help="Reject", use_container_width=True):
                reject_enrollment_request(req['id'])
                st.rerun()