import streamlit as st
from src.database.db import save_attendance


@st.dialog("Attendance Reports", width='large')
def dialog_attendance_report(results, subject_id):
    st.write("Please review attendance before confirming")

    # --- Table header ---
    h1, h2, h3, h4 = st.columns([3, 1, 2, 2])
    with h1: st.markdown("**Name**")
    with h2: st.markdown("**ID**")
    with h3: st.markdown("**Source**")
    with h4: st.markdown("**Status**")

    st.divider()

    # --- Rows ---
    for r in results:
        c1, c2, c3, c4 = st.columns([3, 1, 2, 2])
        with c1: st.write(r['name'])
        with c2: st.write(r['student_id'])
        with c3: st.write(r['source'])
        with c4:
            if r['present']:
                st.success("✅ Present")
            else:
                st.error("❌ Absent")

    st.divider()

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Discard", type="primary", width='stretch'):
            st.rerun()
    with b2:
        if st.button("Confirm & Save", type="primary", width='stretch'):
            save_attendance(results, subject_id)
            st.success("Attendance saved!")
            import time; time.sleep(1)
            st.session_state.added_photos = []
            st.rerun()