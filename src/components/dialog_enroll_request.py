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
    st.caption(f"{count} pending request{'s' if count != 1 else ''}")

    # ── Approve all shortcut (only shown for 2+ requests) ─────────
    if count > 1:
        if st.button(f"✓ Approve all ({count})", use_container_width=True, type="primary"):
            for req in pending_requests:
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
            st.success(f"Approved {count} students!")
            st.rerun()

    st.divider()

    # ── Per-student rows ──────────────────────────────────────────
    for req in pending_requests:
        student_email = req['students'].get('email', '')
        student_name  = req['students'].get('name', student_email)
        initials = ''.join(w[0].upper() for w in student_name.split()[:2])

        # Name row — full width, no columns
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <div style="
                width:28px;height:28px;border-radius:50%;
                background:#e8edf5;flex-shrink:0;
                display:inline-flex;align-items:center;justify-content:center;
                font-size:11px;font-weight:600;color:#4a6fa5;
              ">{initials}</div>
              <span style="font-size:13px;word-break:break-all;">{student_email}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Buttons row — exactly 2 equal columns, always side-by-side on mobile
        col_approve, col_reject = st.columns(2)

        with col_approve:
            if st.button(
                "✓ Approve",
                key=f"approve_{req['id']}",
                use_container_width=True,
                type="primary"
            ):
                approve_enrollment_request(req['id'], req['student_id'], req['subject_id'])
                st.rerun()

        with col_reject:
            if st.button(
                "✕ Reject",
                key=f"reject_{req['id']}",
                use_container_width=True
            ):
                reject_enrollment_request(req['id'])
                st.rerun()

        st.divider()