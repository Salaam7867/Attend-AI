from src.database.config import supabase
import bcrypt


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0


def create_teacher(username, password, name):
    data = { "username": username, "password": hash_pass(password), "name": name }
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_student(name, face_embedding):
    data = { "name": name, "face_embedding": face_embedding }
    response = supabase.table("students").insert(data).execute()
    return response.data[0] if response.data else None

def create_subject(name, subject_code, section, teacher_id):
    data = { "name": name, "subject_code": subject_code, "section": section, "teacher_id": teacher_id }
    response = supabase.table("subjects").insert(data).execute()
    return response.data[0] if response.data else None


def subject_code_exists(subject_code, section):
    response = supabase.table("subjects").select("subject_code,section").eq("subject_code", subject_code).eq("section", section).execute()
    return len(response.data) > 0

def get_subjects_by_teacher(teacher_id):
    response = supabase.table("subjects").select("*").eq("teacher_id", teacher_id).execute()
    return response.data

def enroll_student_to_subject(student_id, subject_id):
    data = { "student_id": student_id, "subject_id": subject_id }
    response = supabase.table("subject_students").insert(data).execute()
    return response.data[0] if response.data else None
