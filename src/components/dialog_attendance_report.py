import streamlit as st
from src.database.db import get_all_students, enroll_student_to_subject
from src.database.config import supabase
import datetime

from src.database.db import save_attendance

@st.dialog('Attendance Reports 📊')
def dialog_attendance_report(df, logs):
    st.write('Please review the attendance report below. You can edit the attendance status for each student before saving the report.')
    st.dataframe(df,hide_index=True,width=700)

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Discard',width = 'stretch'):
            st.info('Attendance report discarded.')
            st.rerun()
    with col2:
        if st.button('Save Report',type= "primary",width = 'stretch'):
            try:
                save_attendance(logs)
                st.success('Attendance report saved successfully.')
                st.rerun()
            except Exception as e:
                st.error(f'Error saving attendance report: {e}')    