import streamlit as st
from utils.db import supabase
import pandas as pd
from src.pipelines.face_pipeline import recognize_face
import cv2

if "page" not in st.session_state:
    st.session_state.page = "login"

st.set_page_config(page_title="SnapClass", layout="centered")
st.sidebar.title("SnapClass")

# ---------------- ROLE SELECTION ----------------
if "role" not in st.session_state:
    role = st.radio("Select Role", ["Student", "Teacher"])
    if st.button("Continue"):
        st.session_state.role = role.lower()
        st.rerun()
    st.stop()

# ---------------- NAVIGATION ----------------
page = st.session_state.page
# ---------------- LOGIN PAGE ----------------
if page == "login":
    st.title("Login Page")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # LOGIN
    if st.button("Login"):
        if email == "" or password == "":
            st.error("Please fill in all fields")
        else:
            user = supabase.table("users") \
                .select("*") \
                .eq("email", email) \
                .eq("password", password) \
                .execute()

            if user.data:
                st.session_state.logged_in = True
                st.session_state.user = user.data[0]
                
                st.success("Login successful!")
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")

    # REGISTER
    if st.button("Register"):
        existing = supabase.table("users") \
            .select("*") \
            .eq("email", email) \
            .execute()

        if existing.data:
            st.error("User already exists")
        else:

            supabase.table("users").insert({
                "email": email,
                "password": password,
                "role": st.session_state.role
            }).execute()

            st.success("Registered successfully")


# ---------------- DASHBOARD ----------------
elif page == "dashboard":
    if st.button("Logout"):
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Please login first")
        st.stop()

    # ===================== TEACHER =====================
    if st.session_state.user["role"] == "teacher":

        st.title("Teacher Dashboard")
        menu = st.radio("Select Action", ["Create Course", "My Courses", "Take Attendance", "View Records"])
        # ---------- CREATE COURSE ----------
        if menu == "Create Course":
            st.subheader("Create Course")
            course_name = st.text_input("Course Code")

            if st.button("Create Course"):
                if course_name == "":
                    st.error("Course code cannot be empty")
                else:
                    existing = supabase.table("courses") \
                        .select("*") \
                        .eq("course_name", course_name) \
                        .execute()

                    if existing.data:
                        st.error("Course already exists")
                    else:
                        supabase.table("courses").insert({
                            "course_name": course_name,
                            "teacher_id": st.session_state.user["id"]
                        }).execute()

                        st.success("Course created successfully")
        # ---------- SHOW CREATED COURSES ----------
        elif menu == "My Courses":
            st.subheader("My Created Courses")

            courses = supabase.table("courses") \
                .select("*") \
                .eq("teacher_id", st.session_state.user["id"]) \
                .execute()

            if not courses.data:
                st.info("No courses created yet")
            else:
                for c in courses.data:
                    st.write("📚", c["course_name"])



        # ---------- TAKE ATTENDANCE (UI ONLY FOR NOW) ----------
        elif menu == "Take Attendance":
            st.subheader("Take Attendance")

            # ✅ FIX: fetch courses again here
            courses = supabase.table("courses") \
                .select("*") \
                .eq("teacher_id", st.session_state.user["id"]) \
                .execute()

            course_names = [c["course_name"] for c in courses.data] if courses.data else []
            
            if course_names:
                selected_course = st.selectbox("Select Course", course_names)
            else:
                st.warning("Create a course first")

            if course_names:

                # get selected course id
                selected_course_obj = [c for c in courses.data if c["course_name"] == selected_course][0]
                course_id = selected_course_obj["id"]

                # fetch enrolled students
                enrollments = supabase.table("enrollments") \
                    .select("*") \
                    .eq("course_id", course_id) \
                    .execute()

                st.subheader("Students")

                if not enrollments.data:
                    st.info("No students enrolled")
                else:
                    attendance_data = []

                    for e in enrollments.data:
                        student = supabase.table("users") \
                            .select("*") \
                            .eq("id", e["student_id"]) \
                            .execute()

                        student_email = student.data[0]["email"]

                        status = st.radio(
                            f"{student_email}",
                            ["Present", "Absent"],
                            key=f"{e['student_id']}"
                        )

                        attendance_data.append({
                            "student_id": e["student_id"],
                            "status": status
                        })

                    # SAVE BUTTON
                    if st.button("Submit Attendance"):

                        from datetime import datetime
                        today = datetime.now().strftime("%Y-%m-%d")

                        for record in attendance_data:
                            existing = supabase.table("attendance") \
                                .select("*") \
                                .eq("student_id", record["student_id"]) \
                                .eq("course_id", course_id) \
                                .eq("date", today) \
                                .execute()

                            if not existing.data:
                                supabase.table("attendance").insert({
                                    "student_id": record["student_id"],
                                    "course_id": course_id,
                                    "status": record["status"],
                                    "date": today
                                }).execute()

                        st.success("Attendance saved")


# ---------------------------- VIEW RECORDS (TEACHER) -------------------- 
        elif menu == "View Records":
            courses = supabase.table("courses") \
                .select("*") \
                .eq("teacher_id", st.session_state.user["id"]) \
                .execute()

            if not courses.data:
                st.warning("No courses")
            else:
                course_names = [c["course_name"] for c in courses.data]
                selected = st.selectbox("Select Course", course_names)

                selected_course = next(c for c in courses.data if c["course_name"] == selected)
                course_id = selected_course["id"]

                attendance = supabase.table("attendance") \
                    .select("*") \
                    .eq("course_id", course_id) \
                    .execute()

                if not attendance.data:
                    st.info("No attendance yet")
                else:    

                    table_data = []

                    for a in attendance.data:
                        student = supabase.table("users") \
                            .select("*") \
                            .eq("id", a["student_id"]) \
                            .execute()

                        email = student.data[0]["email"]

                        table_data.append({
                            "Student": email,
                            "Date": a["date"],
                            "Status": a["status"]
                        })

                    df = pd.DataFrame(table_data)

                    st.table(df)

                    # DOWNLOAD BUTTON
                    if st.button("Download CSV"):
                        df.to_csv("attendance.csv", index=False)
                        st.success("Downloaded")
                        
    
    
    
    
    # ===================== STUDENTS =====================
    elif st.session_state.user["role"] == "student":

        st.title("Student Dashboard")
        menu = st.radio("Select Action", ["Enroll", "My Courses", "View Records"])

        # ---------- ENROLL ----------
        if menu == "Enroll":
            st.subheader("Enroll in Course")

            course_input = st.text_input("Enter Course Code")

            if st.button("Enroll"):
                course = supabase.table("courses") \
                    .select("*") \
                    .eq("course_name", course_input) \
                    .execute()

                if not course.data:
                    st.error("Invalid course code")
                else:
                    course_id = course.data[0]["id"]

                    # check duplicate
                    existing = supabase.table("enrollments") \
                        .select("*") \
                        .eq("student_id", st.session_state.user["id"]) \
                        .eq("course_id", course_id) \
                        .execute()

                    if existing.data:
                        st.warning("Already enrolled")
                    else:
                        supabase.table("enrollments").insert({
                            "student_id": st.session_state.user["id"],
                            "course_id": course_id
                        }).execute()

                        st.success("Enrolled successfully")

        # ---------- MY COURSES ----------
        elif menu == "My Courses":

            st.subheader("My Courses")

            enrollments = supabase.table("enrollments") \
                .select("*") \
                .eq("student_id", st.session_state.user["id"]) \
                .execute()

            if not enrollments.data:
                st.info("No courses enrolled yet")
            else:
                for e in enrollments.data:
                    course = supabase.table("courses") \
                        .select("*") \
                        .eq("id", e["course_id"]) \
                        .execute()

                    if course.data:
                        st.write("📘", course.data[0]["course_name"])


        elif menu == "View Records":
            st.subheader("My Attendance")

            records = supabase.table("attendance") \
                .select("*") \
                .eq("student_id", st.session_state.user["id"]) \
                .execute()

            if not records.data:
                st.info("No attendance records yet")
            else:
                for r in records.data:
                    course = supabase.table("courses") \
                        .select("*") \
                        .eq("id", r["course_id"]) \
                        .execute()

                    course_name = course.data[0]["course_name"]

                    st.write(f"{course_name} | {r['status']} | {r['date']}")

