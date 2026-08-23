import streamlit as st


from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_dashboard, style_background_home
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.screens.home_screen import home_screen


# TEMPORARY SUPABASE CONNECTION TEST
try:
    from supabase import create_client

    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

    supabase = create_client(supabase_url, supabase_key)

    result = supabase.table("students").select("*").limit(1).execute()

    st.success("Supabase connection successful")
    st.write("Students query result:", result.data)

except Exception as e:
    st.error(f"Supabase connection error: {type(e).__name__}: {e}")

st.stop()



def main():
    st.set_page_config(
        page_title="AttendAI - Making Attendance Faster with AI",
        page_icon="https://i.ibb.co/YTYGn5qV/snapclass-logo.png"
        )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case _:
            home_screen()


    # Handle QR code join flow
    join_code = st.query_params.get('subject_code')
    if join_code:
        if st.session_state.get('login_type') != 'student':
            st.session_state['login_type'] = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)

if __name__ == "__main__":
    main()