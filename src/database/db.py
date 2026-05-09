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


def get_student_subjects(student_id):
    response = supabase.table("subject_students").select("subjects(*)").eq("student_id", student_id).execute()
    return response.data

def get_student_attendance(student_id):
    response = supabase.table("attendance_logs").select("*").eq("student_id", student_id).execute()
    return response.data

def unenroll_subject(subject_id):
    response = supabase.table("subject_students").delete().eq("subject_id", subject_id).execute()
    return response.data
    

def get_students_by_subject(subject_id):
    response = supabase.table("subject_students")\
        .select("student_id, students(student_id, name)")\
        .eq("subject_id", subject_id).execute()
    return [
        {'student_id': r['students']['student_id'], 'name': r['students']['name']} 
        for r in response.data if r.get('students')
    ]

def save_attendance(attendance_logs):
    # attendance_logs is a list of dicts with keys: student_id, subject_id, timestamp, is_present
    data = [
        {
            "student_id": log['student_id'],
            "subject_id": log['subject_id'],
            "timestamp": log.get('timestamp'),
            "is_present": log['status'].lower() == 'present'  # store as boolean
        }
        for log in attendance_logs
    ]
    response = supabase.table("attendance_logs").insert(data).execute()
    return response.data


def get_student_count_by_subject(subject_id):
    response = supabase.table("subject_students")\
        .select("student_id")\
        .eq("subject_id", subject_id).execute()
    return len(response.data)


def get_class_count_by_subject(subject_id):
    response = supabase.table("attendance_logs")\
        .select("timestamp")\
        .eq("subject_id", subject_id).execute()
    # Count distinct timestamps = distinct sessions
    timestamps = set(r['timestamp'] for r in response.data)
    return len(timestamps)




def get_attendance_sessions_by_teacher(teacher_id):
    # Step 1 — get all subject_ids for this teacher
    subjects_response = supabase.table("subjects")\
        .select("subject_id, name, section, subject_code")\
        .eq("teacher_id", teacher_id).execute()
    
    if not subjects_response.data:
        return []

    # Build a lookup: subject_id -> {name, section}
    # To this — add subject_code
    subject_map = {
        s['subject_id']: {'name': s['name'], 'section': s['section'], 'subject_code': s['subject_code']}
        for s in subjects_response.data
    }
    subject_ids = list(subject_map.keys())

    # Step 2 — get all logs for those subjects
    logs_response = supabase.table("attendance_logs")\
        .select("subject_id, timestamp, is_present")\
        .in_("subject_id", subject_ids).execute()

    if not logs_response.data:
        return []

    # Step 3 — group by (subject_id + timestamp)
    sessions = {}
    for log in logs_response.data:
        key = (log['subject_id'], log['timestamp'])
        if key not in sessions:
            sessions[key] = {'present': 0, 'total': 0}
        sessions[key]['total'] += 1
        if log['is_present']:
            sessions[key]['present'] += 1

    # Step 4 — build final list
    result = []
    for (subject_id, timestamp), counts in sessions.items():
        subject_info = subject_map[subject_id]
        result.append({
            'subject_id': subject_id,
            'name': subject_info['name'],
            'section': subject_info['section'],
            'subject_code': subject_info['subject_code'],
            'timestamp': timestamp,
            'present': counts['present'],
            'total': counts['total']
        })

    # Sort by most recent first
    result.sort(key=lambda x: x['timestamp'], reverse=True)
    return result


def get_session_detail(subject_id, timestamp):
    # Get all logs for this specific session
    response = supabase.table("attendance_logs")\
        .select("student_id, is_present, students(name)")\
        .eq("subject_id", subject_id)\
        .eq("timestamp", timestamp).execute()

    return [
        {
            'student_id': r['student_id'],
            'name': r['students']['name'] if r.get('students') else f"Student {r['student_id']}",
            'is_present': r['is_present']
        }
        for r in response.data
    ]