import streamlit as st
from src.database.config import supabase
from src.database.db import get_pending_requests, approve_enrollment_request, reject_enrollment_request

@st.dialog("Enrollment Requests")
def enrollment_requests_dialog(subject):

    st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 !important;
    }
    /* Remove excess spacing between elements */
    .stMarkdown { margin-bottom: 0 !important; }
    .stButton  { margin-top: 4px !important; }
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

    for req in pending_requests:
        student_email = req['students'].get('email', '')
        student_name  = req['students'].get('name', student_email)
        initials = ''.join(w[0].upper() for w in student_name.split()[:2])

        st.markdown('<hr style="border:none;border-top:1px solid rgba(128,128,128,0.2);margin:8px 0">', unsafe_allow_html=True)

        # ── Avatar + name: native st.write for the text ──────────
        col_info, col_spacer = st.columns([1, 10])
        with col_info:
            st.markdown(
                f'<div style="width:28px;height:28px;border-radius:50%;'
                f'background:rgba(100,120,200,0.15);display:flex;'
                f'align-items:center;justify-content:center;'
                f'font-size:11px;font-weight:600;color:#6478c8;margin-top:4px">'
                f'{initials}</div>',
                unsafe_allow_html=True
            )
        with col_spacer:
            # Native st.write — always respects light/dark theme
            st.write(student_email)

        # ── Action buttons ────────────────────────────────────────
        col_approve, col_reject = st.columns(2)

        with col_approve:
            if st.button("✓ Approve", key=f"approve_{req['id']}",
                         use_container_width=True, type="primary"):
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
                st.rerun()

        with col_reject:
            if st.button("✕ Reject", key=f"reject_{req['id']}",
                         use_container_width=True):
                reject_enrollment_request(req['id'])
                st.rerun()