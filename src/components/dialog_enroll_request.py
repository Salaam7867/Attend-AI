import streamlit as st
from src.database.config import supabase
from src.database.db import get_pending_requests, approve_enrollment_request, reject_enrollment_request

@st.dialog("Enrollment Requests")
def enrollment_requests_dialog(subject):

    st.markdown("""
    <style>
    /* Keep columns side-by-side on mobile */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 !important;
        width: auto !important;
    }
    /* Shrink the default padding Streamlit adds between elements */
    [data-testid="stVerticalBlockBorderWrapper"] > div > div {
        gap: 0 !important;
    }
    .req-divider {
        border: none;
        border-top: 1px solid rgba(128,128,128,0.15);
        margin: 6px 0 10px 0;
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

    for req in pending_requests:
        student_email = req['students'].get('email', '')
        student_name  = req['students'].get('name', student_email)
        initials = ''.join(w[0].upper() for w in student_name.split()[:2])

        # thin divider between rows (no st.divider() = no huge gap)
        st.markdown('<hr class="req-divider">', unsafe_allow_html=True)

        # Name row — color uses `currentColor` so it works in light + dark mode
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:8px;margin:4px 0 6px 0;">
              <div style="
                width:26px;height:26px;border-radius:50%;
                background:rgba(100,120,200,0.15);flex-shrink:0;
                display:inline-flex;align-items:center;justify-content:center;
                font-size:11px;font-weight:600;
                color:rgba(100,120,200,0.9);
              ">{initials}</div>
              <span style="font-size:13px;word-break:break-all;
                color:inherit;
              ">{student_email}</span>
            </div>""",
            unsafe_allow_html=True
        )

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