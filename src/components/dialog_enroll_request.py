import streamlit as st
from src.database.config import supabase
from src.database.db import get_pending_requests, approve_enrollment_request, reject_enrollment_request

@st.dialog("Enrollment Requests")
def enrollment_requests_dialog(subject):
    pending_requests = get_pending_requests(subject['subject_id'])

    if not pending_requests:
        st.info("No pending requests.")
        return

    count = len(pending_requests)
    st.markdown(
        f"<p style='color:var(--text-color);font-size:13px;margin:0 0 8px'>"
        f"<b>{count}</b> pending request{'s' if count != 1 else ''}</p>",
        unsafe_allow_html=True
    )

    # ── Approve all shortcut ──────────────────────────────────────
    if count > 1:
        if st.button(f"✓ Approve all ({count})", use_container_width=True, type="primary"):
            for req in pending_requests:
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
            st.success(f"Approved {count} students!")
            st.rerun()

    st.divider()

    # ── Per-student compact rows ──────────────────────────────────
    for req in pending_requests:
        student_email = req['students'].get('email', '')
        student_name  = req['students'].get('name', student_email)
        initials = ''.join(w[0].upper() for w in student_name.split()[:2])

        # Name + initials avatar on the left
        col_name, col_approve, col_reject = st.columns([5, 1, 1])

        with col_name:
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:8px;padding:4px 0">
                  <div style="
                    width:28px;height:28px;border-radius:50%;
                    background:#e8edf5;display:inline-flex;
                    align-items:center;justify-content:center;
                    font-size:11px;font-weight:600;color:#4a6fa5;
                    flex-shrink:0;
                  ">{initials}</div>
                  <span style="font-size:13px;word-break:break-all;">{student_email}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_approve:
            if st.button("✓", key=f"approve_{req['id']}", help="Approve",
                         use_container_width=True, type="primary"):
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
                st.rerun()

        with col_reject:
            if st.button("✕", key=f"reject_{req['id']}", help="Reject",
                         use_container_width=True):
                reject_enrollment_request(req['id'])
                st.rerun()
                # st.warning(f"Rejected {student_email}")