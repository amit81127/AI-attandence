from src.database.config import supabase
import bcrypt


def hash_pass(pwd):
    return bcrypt.hashpw(
        pwd.encode(),
        bcrypt.gensalt()
    ).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(
        pwd.encode(),
        hashed.encode()
    )


def check_teacher_exists(username):
    response = (
        supabase
        .table("teachers")
        .select("username")
        .ilike("username", username.strip())
        .execute()
    )

    return len(response.data) > 0


def create_teacher(username, name, password):
    data = {
        "username": username.strip(),
        "name": name.strip(),
        "password": hash_pass(password)
    }

    response = (
        supabase
        .table("teachers")
        .insert(data)
        .execute()
    )

    return response.data


def teacher_login(username, password):
    try:
        response = (
            supabase
            .table("teachers")
            .select("*")
            .ilike("username", username.strip())
            .execute()
        )

        if response.data:
            teacher = response.data[0]

            if check_pass(password, teacher["password"]):
                return teacher
    except Exception as e:
        print(f"Error during teacher_login: {e}")

    return None

def get_all_students():
    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return response.data

def create_student(name, face_embedding=None, voice_embedding=None):
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }
    
    response = supabase.table("students").insert(data).execute()

    return response.data


def create_subject(subject_code,name,section,teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }
    
    response = supabase.table("subjects").insert(data).execute()

    return response.data

def get_teacher_subject(teacher_id):
    if not teacher_id:
        return []
    try:
        response = supabase.table('subjects').select("*,subject_students(count),attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
        subjects = response.data or []

        for sub in subjects:
            sub_students = sub.get("subject_students")
            if sub_students and len(sub_students) > 0:
                sub['total_students'] = sub_students[0].get('count', 0)
            else:
                sub['total_students'] = 0
            
            attendance = sub.get("attendance_logs", []) or []
            unique_sessions = len(set(log['timestamp'] for log in attendance if 'timestamp' in log))
            sub['total_classes'] = unique_sessions
            
            sub.pop('subject_students', None)
            sub.pop('attendance_logs', None)

        return subjects
    except Exception as e:
        print(f"Error in get_teacher_subject: {e}")
        return []
        
def enroll_student_to_subject(student_id,subject_id):
    data={'student_id':student_id,"subject_id":subject_id}
    response=supabase.table("subject_students").insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id,subject_id):
    response=supabase.table('subject_students').delete().eq("student_id",student_id).eq("subject_id",subject_id).execute()
    return response.data


def get_student_subject(student_id):
    if not student_id:
        return []
    try:
        response = (
            supabase
            .table('subject_students')
            .select("*,subjects(*)")
            .eq("student_id", student_id)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error in get_student_subject: {e}")
        return []

# Backwards compatibility alias
get_students_subject = get_student_subject


def get_student_attendance(student_id):
    if not student_id:
        return []
    try:
        response = (
            supabase
            .table('attendance_logs')
            .select("*,subjects(*)")
            .eq("student_id", student_id)
            .execute()
        )
        return response.data or []
    except Exception:
        try:
            response = (
                supabase
                .table('attendence_logs')
                .select("*,subjects(*)")
                .eq("student_id", student_id)
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"Error in get_student_attendance: {e}")
            return []

# Backwards compatibility aliases
get_students_attandence = get_student_attendance
get_student_attandence = get_student_attendance
get_students_attendance = get_student_attendance