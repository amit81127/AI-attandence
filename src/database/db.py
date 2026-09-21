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