import streamlit as st

from src.components import dialog_create_subject
from src.components.dialog_create_subject import dialog_create_subject
from src.components.dialog_share_subject import share_subject_dialog   
from src.components.dialog_attendance import dialog_attendance
from src.components.dialog_attendance_report import dialog_attendance_report
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exists, create_teacher, get_class_count_by_subject, teacher_login, get_subjects_by_teacher,get_student_count_by_subject
from src.pipelines.face_pipeline import predict_attendance
from src.database.db import get_students_by_subject
from src.database.db import get_attendance_sessions_by_teacher, get_session_detail
import numpy as np
import pandas as pd
from PIL import Image
from datetime import datetime

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
    header_dashboard()


    logout_col1, logout_col2, logout_col3 = st.columns([1,2,1])

    with logout_col1:
        #st.image("https://i.ibb.co/YTYGn5qV/snapclass-logo.png", width=40)
        st.header(f"Welcome, {st.session_state.teacher_data['name']}!")
        
    with logout_col3:
        if st.button(
            "Logout",
            type='secondary',
            key='logoutbtn',
            width='stretch',
            shortcut="control+shift+backspace"
        ):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.teacher_data = None
            st.session_state.teacher_login_type = 'login'
            st.rerun()


    # ---------- TAB STATE ----------
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    # ---------- TAB BUTTONS ----------
    tab1, tab2, tab3 = st.columns(3,vertical_alignment='center', gap='small')

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
    
                # Step 1 — Get enrolled students for THIS subject (this is the base list)
                enrolled = get_students_by_subject(selected_subject['subject_id'])
                
                if not enrolled:
                    st.warning("No students enrolled in this subject yet!")
                else:
                    # student_id -> list of photos they were found in
                    all_detected = {}
                    total_faces = 0

                    with st.spinner("Scanning photos for faces..."):
                        for i, photo in enumerate(st.session_state.added_photos):
                            img = Image.open(photo).convert("RGB")
                            img_np = np.array(img)
                            detected, _, face_count = predict_attendance(img_np)
                            
                            total_faces += face_count
                            for student_id in detected:
                                # Convert to int to ensure type match
                                sid = int(student_id)
                                if sid not in all_detected:
                                    all_detected[sid] = []
                                all_detected[sid].append(f"Photo {i+1}")

                    # Step 2 — Build results from enrolled list, not SVM list
                    results = []
                    attendance_to_log =[]

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for student in enrolled:
                        sid = int(student['student_id'])
                        is_present = sid in all_detected
                        results.append({
                            'Name': student['name'],   # real name from DB
                            'Student_id': sid,
                            'Source': ", ".join(all_detected[sid]) if is_present else "—",
                            'Status': "Present" if is_present else "Absent"
                        })

                        attendance_to_log.append({
                            'student_id': sid,
                            'subject_id': selected_subject['subject_id'],
                            'timestamp': current_timestamp,
                            'status': "Present" if is_present else "Absent"
                            
                        })

                    dialog_attendance_report(results, attendance_to_log)


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
                student_count = get_student_count_by_subject(subject['subject_id'])
                class_count = get_class_count_by_subject(subject['subject_id'])
                st.markdown(f"**Code:** `{subject['subject_code']}` | **Section:** {subject['section']}")
                st.markdown(f"👥 {student_count} Students &nbsp;&nbsp; 🎓 {class_count} Classes")
            with col2:
                if st.button(f"Share Code : {subject['name']}", 
                            key=f"share_{subject['subject_id']}", 
                            type='secondary',
                            icon=':material/share:'):
                    share_subject_dialog(subject)
            


def teacher_tab_attendance_records():
    st.header("Attendance Records")
    teacher_id = st.session_state.teacher_data['teacher_id']

    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = None

    # ---------- VIEW 2 ----------
    if st.session_state.selected_session:
        session = st.session_state.selected_session

        if st.button("← Back to all sessions", type='tertiary'):
            st.session_state.selected_session = None
            st.rerun()

        st.subheader(f"{session['name']} — `{session['subject_code']}` — Section {session['section']}")
        st.caption(session['timestamp'])

        enrolled = get_student_count_by_subject(session['subject_id'])
        present = session['present']
        rate = round((present / enrolled * 100)) if enrolled > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Enrolled", enrolled)
        c2.metric("Attended", f"{present}/{enrolled}")
        c3.metric("Attendance Rate", f"{rate}%")

        st.divider()

        detail = get_session_detail(session['subject_id'], session['timestamp'])

        if not detail:
            st.info("No student data found for this session.")
            return

        rows = []
        for student in detail:
            rows.append({
                'Student': student['name'],
                'ID': student['student_id'],
                'Status': '✅ Present' if student['is_present'] else '❌ Absent'
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, hide_index=True, use_container_width=True)
        return

    # ---------- VIEW 1 ----------
    sessions = get_attendance_sessions_by_teacher(teacher_id)

    if not sessions:
        st.info("No attendance sessions recorded yet.")
        return

    subjects = get_subjects_by_teacher(teacher_id)
    subject_options = {"All subjects": None}
    for s in subjects:
        subject_options[f"{s['name']} ({s['section']})"] = s['subject_id']

    selected_filter = st.selectbox("Filter by subject", options=list(subject_options.keys()), label_visibility='collapsed')
    filtered_id = subject_options[selected_filter]

    filtered_sessions = [s for s in sessions if s['subject_id'] == filtered_id] if filtered_id else sessions

    total_sessions = len(filtered_sessions)
    avg_attendance = round(sum(s['present'] / s['total'] * 100 for s in filtered_sessions if s['total'] > 0) / total_sessions) if total_sessions > 0 else 0
    enrolled_count = get_student_count_by_subject(filtered_id) if filtered_id else "—"

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sessions", total_sessions)
    c2.metric("Avg Attendance", f"{avg_attendance}%")
    c3.metric("Enrolled Students", enrolled_count)

    st.divider()

    rows = []
    for session in filtered_sessions:
        ts = datetime.fromisoformat(session['timestamp'].replace("Z", "+00:00"))
        rows.append({
            'Subject': session['name'],
            'Code': session['subject_code'],
            'Section': session['section'],
            'Date & Time': ts.strftime("%d %b %Y, %I:%M %p"),
            'Attended': f"{session['present']}/{session['total']}",
        })

    df = pd.DataFrame(rows)

    st.info("☑️ Click the box on the left of a row to view session details")
    event = st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        on_select='rerun',
        selection_mode='single-row'
    )

    if event.selection.rows:
        selected_index = event.selection.rows[0]
        st.session_state.selected_session = filtered_sessions[selected_index]
        st.rerun()

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

def teacher_register(email, name, password, password_confirm):
    if password != password_confirm:
        return False, "Passwords do not match"
    
    if check_teacher_exists(email):
        return False, "Email already taken"
    if not email or not name or not password:
        return False, "All fields are required"
    create_teacher(email, password, name)
    return True, "Registration successful! Please login now."
"""
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
    teacher_email = st.text_input("Enter email", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_email, teacher_pass):
                st.toast("Login successful!")
                import time
                time.sleep(1)   
                st.rerun()
            else:
                st.error("Invalid email or password")
    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state['teacher_login_type'] = 'register'
            st.rerun()
        
    footer_dashboard()
"""



def teacher_screen_login():
    st.markdown("""
    <style>
    .login-header {
        background: #534AB7;
        padding: 2rem 1.5rem 1.5rem;
        border-radius: 16px 16px 0 0;
        margin-bottom: 0;
    }
    .login-header h1 { color: #EEEDFE; font-size: 22px; font-weight: 500; margin: 0 0 4px; }
    .login-header p { color: #AFA9EC; font-size: 13px; margin: 0; }
    .login-logo { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; }
    .login-logo span { color: #EEEDFE; font-size: 16px; font-weight: 500; }
    </style>

    <div class="login-header">
        <div class="login-logo">
            <img src="https://i.ibb.co/YTYGn5qV/snapclass-logo.png"
                style="width:52px;height:52px;border-radius:12px;">
            <span>Attend AI</span>
        </div>
        <h2>Welcome back</h2>
        <p>AI-powered attendance for modern classrooms</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Login to your account")

        teacher_email = st.text_input("Email", placeholder='teacher@school.com')
        teacher_pass = st.text_input("Password", type='password', placeholder="Enter password")

        st.space()

        
        if st.button('Login', type='primary', icon=':material/login:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_email, teacher_pass):
                st.toast("Login successful!")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid email or password")

        st.markdown(
            "<p style='text-align:center; color:#999; opacity:0.6;'>--------------- or ---------------</p>",
            unsafe_allow_html=True
        )

        if st.button('Create account', type='secondary', width='stretch'):
            st.session_state['teacher_login_type'] = 'register'
            st.rerun()

        st.divider()
        if st.button("← Back to Home", type='tertiary', width='stretch'):
            st.session_state['login_type'] = None
            st.rerun()

    footer_dashboard()


def teacher_screen_register():
    st.markdown("""
    <style>
    .login-header {
        background: #534AB7;
        padding: 2.5rem 1.8rem 1.8rem;
        border-radius: 16px 16px 0 0;
    }
    .login-header h2 { color: #EEEDFE; font-size: 22px; font-weight: 500; margin: 0 0 4px; }
    .login-header p { color: #AFA9EC; font-size: 13px; margin: 0; }
    .login-logo { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; }
    .login-logo span { color: #EEEDFE; font-size: 18px; font-weight: 500; }
    </style>

    <div class="login-header">
        <div class="login-logo">
            <img src="https://i.ibb.co/YTYGn5qV/snapclass-logo.png"
                style="width:52px;height:52px;border-radius:12px;">
            <span>Attend AI</span>
        </div>
        <h2>Create account</h2>
        <p>Join teachers using AI-powered attendance</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Set up your teacher profile")

        teacher_name = st.text_input("Full name", placeholder='Ananya Roy')
        teacher_email = st.text_input("Email", placeholder='teacher@school.com')
        teacher_pass = st.text_input("Password", type='password', placeholder="Enter password")
        teacher_pass_confirm = st.text_input("Confirm password", type='password', placeholder="Repeat password")

        st.space()

        if st.button(
            'Create account →',
            type='primary',
            icon=':material/person_add:',
            width='stretch'
        ):

            success, message = teacher_register(
                teacher_email,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm
            )

            if success:
                st.success(message)

                import time
                time.sleep(2)

                st.session_state.teacher_login_type = 'login'
                st.rerun()

            else:
                st.error(message)


        st.markdown(
            "<p style='text-align:center; color:#999; opacity:0.6;'>--------------- or ---------------</p>",
            unsafe_allow_html=True
        )


        if st.button(
            'Login instead',
            type='secondary',
            width='stretch',
            icon=':material/login:'
        ):
            st.session_state.teacher_login_type = 'login'
            st.rerun()

"""
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

    teacher_email = st.text_input("Enter email", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = teacher_register(teacher_email, teacher_name, teacher_pass, teacher_pass_confirm)
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

    
"""