import streamlit as st


from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_dashboard, style_background_home
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen
from src.screens.home_screen import home_screen


def main():

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case _:
            home_screen()

if __name__ == "__main__":
    main()