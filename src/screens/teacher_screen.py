import streamlit as st

from src.components import dialog_create_subject
from src.components.dialog_create_subject import dialog_create_subject
from src.components.dialog_share_subject import share_subject_dialog   
from src.components.dialog_attendance import dialog_attendance
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_subjects_by_teacher     


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    # ---------- INIT SESSION STATE ----------
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

    if 'teacher_data' not in st.session_state:
        st.session_state.teacher_data = None

    if 'teacher_login_type' not in st.session_state:
        st.session_state.teacher_login_type = 'login'


    # ---------- MAIN LOGIC ----------
    if st.session_state.logged_in and st.session_state.user_role == 'teacher':
        teacher_dashboard()
    else:
        if st.session_state.teacher_login_type == 'login':
            teacher_screen_login()
        elif st.session_state.teacher_login_type == 'register':
            teacher_screen_register()




def teacher_dashboard():
    st.header(f"Welcome, {st.session_state.teacher_data['name']}!", text_alignment='center')
    c1,c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()  
    with c2:
        st.space()
        st.subheader(f"Welcome, {st.session_state.teacher_data['name']}!", text_alignment='center')
        if st.button("Logout", type='secondary', key='logoutbtn', shortcut="control+shift+backspace"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.teacher_data = None
            st.session_state.teacher_login_type = 'login'
            st.rerun()


        st.space()


    # ---------- TAB STATE ----------
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    # ---------- TAB BUTTONS ----------
    tab1, tab2, tab3 = st.columns(3,vertical_alignment='center', gap='large')

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
        if st.button("Take Attendance", type=type1, width="stretch", icon=":material/ar_on_you:"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=type2, width="stretch", icon=":material/book_ribbon:"):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
        if st.button("Attendance Records", type=type3, width="stretch", icon=":material/cards_stack:"):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

   

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()


    footer_dashboard()


def teacher_tab_take_attendance():
    st.header("Take Attendance")
    
    teacher_id = st.session_state.teacher_data['teacher_id']
    subjects = get_subjects_by_teacher(teacher_id)

    if not subjects:
        st.info("No subjects created yet! Create one in 'Manage Subjects'.")
        return

    subject_options = {f"{s['name']} ({s['section']})": s for s in subjects}

    c1, c2 = st.columns([3,1], vertical_alignment='bottom')
    with c1:
        selected_label = st.selectbox("Select Subject", options=list(subject_options.keys()))
        selected_subject = subject_options[selected_label]
    with c2:
        if st.button("Start Attendance", type='primary', icon=':material/ar_on_you:'):
            dialog_attendance(selected_subject['subject_id'])

    # --- Added Photos (on main page, below the selectbox) ---
    if st.session_state.get('added_photos'):
        st.divider()
        st.subheader("Added Photos")
        cols = st.columns(3)
        for i, photo in enumerate(st.session_state.added_photos):
            with cols[i % 3]:
                st.image(photo, caption=f"Photo {i+1}", use_container_width=True)

        st.divider()
        b1, b2 = st.columns(2, gap='small')
        with b1:
            if st.button("Clear all photos", type="tertiary", width='stretch', icon=':material/delete:'):
                st.session_state.added_photos = []
                st.rerun()
        with b2:
            if st.button("Run Face Analysis", type="primary", width='stretch', icon=':material/face:'):
                st.info("Processing photos for attendance...")
                # Here you would call your face recognition pipeline with the added photos
                # For example: results = predict_attendance(st.session_state.added_photos, selected_subject['subject_id'])
                # Then you can display the results or save them to the database
        

def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        st.header("Manage Subjects")
    with c2:
        if st.button("Create New Subject", type='primary', icon=':material/add:'):
            dialog_create_subject(teacher_id)


    # ---------- SUBJECT CARDS ----------
    subjects = get_subjects_by_teacher(teacher_id)

    if not subjects:
        st.info("No subjects created yet!")
        return
    
    for subject in subjects:
        with st.container(border=True):
            
            st.subheader(subject['name'])

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Code:** `{subject['subject_code']}` | **Section:** {subject['section']}")
                st.markdown(f"👥 {subject.get('student_count', 0)} Students &nbsp;&nbsp; 🎓 {subject.get('class_count', 0)} Classes")
            
            with col2:
                if st.button(f"Share Code : {subject['name']}", 
                            key=f"share_{subject['subject_id']}", 
                            type='secondary',
                            icon=':material/share:'):
                    share_subject_dialog(subject)
            

def teacher_tab_attendance_records():
    st.header("Attendance Records")
    teacher_data = st.session_state.teacher_data





def login_teacher(username, password):
    if not username or not password:
        st.error("Please enter both username and password")
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.logged_in = True
        return True
    return False

def teacher_register(username, name, password, password_confirm):
    if password != password_confirm:
        return False, "Passwords do not match"
    
    if check_teacher_exists(username):
        return False, "Username already taken"
    if not username or not name or not password:
        return False, "All fields are required"
    create_teacher(username, password, name)
    return True, "Registration successful! Please login now."

def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['teacher_login_type'] = 'login'
            st.rerun()


    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Login successful!")
                import time
                time.sleep(1)   
                st.rerun()
            else:
                st.error("Invalid username or password")
    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state['teacher_login_type'] = 'register'
            st.rerun()
        
    footer_dashboard()


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Register your teacher profile')
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = teacher_register(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                
                st.session_state.teacher_login_type = 'login'
                time.sleep(2)
                st.rerun()
            else:                
                st.error(message)
    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'
            st.rerun()

    footer_dashboard()
