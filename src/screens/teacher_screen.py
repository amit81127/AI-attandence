import streamlit as st
from src.ui.style_base_layout import style_background_dashboard, style_base_layout
from src.components.footer import footer_home
from src.components.header import header_dashboard

from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subject
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_add_photo import add_photo_dialog
from src.components.dialog_attendance_result import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog

from src.pipelines.face_pipeline import predict_attendance

import numpy as np
from datetime import datetime
from src.database.config import supabase
import pandas as pd
import time


def teacher_screen():
    style_background_dashboard()
    style_base_layout()
    
    if 'teacher_login_type' not in st.session_state:
        st.session_state['teacher_login_type'] = "login"
        
    if st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()
    elif st.session_state.teacher_login_type == "dashboard":
        teacher_dashboard()
    
      
def teacher_screen_login():
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()
            
    st.header("Login using password", text_alignment='center')
    st.write("")
    st.write("")

    with st.form(key="teacher_login_form"):
        teacher_username = st.text_input("Enter username", placeholder="ananyaroy", key="login_user_input")
        teacher_pass = st.text_input("Enter password", placeholder="*********", type='password', key="login_pass_input")
        
        st.divider()

        submit_login = st.form_submit_button("Login", icon=':material/passkey:', shortcut='control+enter', use_container_width=True)

    if submit_login:
        username_clean = teacher_username.strip()
        if not username_clean or not teacher_pass:
            st.error("Please enter both username and password!")
        else:
            teacher = teacher_login(username_clean, teacher_pass)
            if teacher:
                st.session_state['teacher_data'] = teacher
                st.session_state['teacher_user'] = teacher
                st.session_state['is_logged_in'] = True
                st.session_state['user_role'] = 'teacher'
                st.session_state['teacher_login_type'] = 'dashboard'
                st.toast(f"Welcome back {teacher.get('name', 'Teacher')}!", icon='🎉')
                st.rerun()
            else:
                st.error("Wrong username or password")

    st.write("")
    if st.button("Register Instead", icon=':material/person_add:', type='primary', key="reg_instead_btn", use_container_width=True):
        st.session_state['teacher_login_type'] = 'register'
        st.rerun()

    footer_home()


def teacher_dashboard():
    teacher = st.session_state.get('teacher_data') or st.session_state.get('teacher_user', {})
    teacher_name = teacher.get('name', 'Teacher')
    
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome {teacher_name}")
        if st.button("Logout", type='secondary', key='teacher_logout_btn', shortcut='control+backspace'):
            st.session_state['is_logged_in'] = False
            st.session_state.pop('teacher_data', None)
            st.session_state.pop('teacher_user', None)
            st.session_state['teacher_login_type'] = 'login'
            st.session_state['login_type'] = None
            st.rerun()
           

    st.write("")

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendence'
    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendence' else "tertiary"
        if st.button("Take Attendance", use_container_width=True, type=type1, icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendence'
            st.rerun()
    
    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button("Manage Subjects", use_container_width=True, type=type2, icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
           
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendence_records' else "tertiary"
        if st.button("Attendance Records", use_container_width=True, type=type3, icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendence_records'
            st.rerun()

    st.divider()
    
    if st.session_state.current_teacher_tab == 'take_attendence':
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == 'attendence_records':
        teacher_tab_attendance_records()
        
    footer_home()


def teacher_tab_take_attendance():
    teacher_data = st.session_state.get('teacher_data') or st.session_state.get('teacher_user', {})
    teacher_id = teacher_data.get('teacher_id') or teacher_data.get('id')
    st.header("Take Attendance")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []
    
    subjects = get_teacher_subject(teacher_id)
    
    if not subjects:
        st.warning("You haven't created any subject yet! Please create one to begin.")
        return

    subject_options = {f"{s.get('subject_code', '')} - {s.get('name', 'Subject')} ({s.get('section', '')})": s.get('subject_id') for s in subjects}
    
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=":material/add_a_photo:", use_container_width=True):
            add_photo_dialog()

    selected_subject_id = subject_options.get(selected_subject_label)

    if st.session_state.attendance_images:
        st.write("")
        st.subheader(f"Captured Photos ({len(st.session_state.attendance_images)})")
        img_cols = st.columns(min(len(st.session_state.attendance_images), 4))
        for idx, img in enumerate(st.session_state.attendance_images):
            with img_cols[idx % 4]:
                st.image(img, use_container_width=True, caption=f"Photo {idx + 1}")

    st.write("")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.session_state.attendance_images:
            if st.button('Clear All Photos', type='secondary', icon=':material/delete:', use_container_width=True):
                st.session_state.attendance_images = []
                st.rerun()

    with c2:
        if st.button('Run Face Analysis', type='secondary', icon=':material/analytics:', use_container_width=True):
            if not st.session_state.attendance_images:
                st.warning("Please add at least one photo first!")
            elif not selected_subject_id:
                st.warning("Please select a subject!")
            else:
                with st.spinner('Analyzing Faces...'):
                    all_detected_ids = {}
                    for idx, img in enumerate(st.session_state.attendance_images):
                        img_np = np.array(img.convert('RGB'))
                        detected, _, _ = predict_attendance(img_np)
                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)
                                all_detected_ids.setdefault(student_id, []).append(f"Photo {idx + 1}")

                    enrolled_res = (
                        supabase
                        .table('subject_students')
                        .select('*,students(*)')
                        .eq('subject_id', selected_subject_id)
                        .execute()
                    )
                    enrolled_students = enrolled_res.data or []

                    if not enrolled_students:
                        st.warning("No students enrolled in this course")
                    else:
                        results, attendance_to_log = [], []
                        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        for node in enrolled_students:
                            student = node.get('students')
                            if not student:
                                continue
                            sid = int(student.get('student_id') or student.get('id'))
                            sources = all_detected_ids.get(sid, [])
                            is_present = len(sources) > 0

                            results.append({
                                "Name": student.get('name', 'Unknown'),
                                "ID": sid,
                                "Source": ", ".join(sources) if is_present else "-",
                                "Status": "Present" if is_present else "Absent"
                            })
                            attendance_to_log.append({
                                'student_id': sid,
                                'subject_id': selected_subject_id,
                                'timestamp': current_timestamp,
                                'is_present': bool(is_present)
                            })
                        attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', icon=':material/mic:', use_container_width=True):
            if selected_subject_id:
                voice_attendance_dialog(selected_subject_id)
            else:
                st.warning("Please select a subject first.")

    st.divider()


def teacher_tab_manage_subjects():
    teacher_data = st.session_state.get('teacher_data') or st.session_state.get('teacher_user', {})
    teacher_id = teacher_data.get('teacher_id') or teacher_data.get('id')
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects")
    with col2:
        if st.button("Add New Subject", icon=':material/add:', type='primary'):
            if teacher_id:
                create_subject_dialog(teacher_id)
            else:
                st.error("Teacher ID not found. Please log in again.")

    subjects = get_teacher_subject(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                {"icon": "🤖", "label": "Students", "value": sub.get('total_students', 0)},
                {"icon": "📋", "label": "Classes", "value": sub.get('total_classes', 0)}
            ]

            def make_share_btn(subject_info):
                def share_btn():
                    if st.button(f"Share Code: {subject_info['name']}", key=f"share_{subject_info['subject_code']}", icon=":material/share:"):
                        share_subject_dialog(subject_info['name'], subject_info['subject_code'])
                return share_btn

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=make_share_btn(sub),
                footer_label="Share Subject"
            )
    else:
        st.info("No subjects found. Click 'Add New Subject' to create one.")


def teacher_tab_attendance_records():
    teacher_data = st.session_state.get('teacher_data') or st.session_state.get('teacher_user', {})
    teacher_id = teacher_data.get('teacher_id') or teacher_data.get('id')
    st.header("Attendance Records")

    subjects = get_teacher_subject(teacher_id)
    if not subjects:
        st.info("No subjects found. Please create a subject first.")
        return

    subject_options = {f"{s.get('subject_code', '')} - {s.get('name', 'Subject')} ({s.get('section', '')})": s.get('subject_id') for s in subjects}
    selected_subject_label = st.selectbox('Select Subject to View Records', options=list(subject_options.keys()), key='records_subject_select')
    selected_subject_id = subject_options.get(selected_subject_label)

    if selected_subject_id:
        with st.spinner("Loading attendance logs..."):
            try:
                res = (
                    supabase
                    .table('attendance_logs')
                    .select('*,students(*)')
                    .eq('subject_id', selected_subject_id)
                    .order('timestamp', desc=True)
                    .execute()
                )
                logs = res.data or []
            except Exception as e:
                st.error(f"Error fetching logs: {e}")
                logs = []

        if logs:
            records = []
            for log in logs:
                student = log.get('students') or {}
                status_val = log.get('status')
                if status_val is None:
                    status_val = log.get('is_present', True)
                status_str = "Present" if status_val else "Absent"
                records.append({
                    "Timestamp": log.get('timestamp', '-'),
                    "Student ID": log.get('student_id', student.get('student_id', '-')),
                    "Student Name": student.get('name', 'Unknown'),
                    "Status": status_str
                })

            df = pd.DataFrame(records)
            
            total_records = len(df)
            present_count = len(df[df['Status'] == 'Present'])
            unique_sessions = df['Timestamp'].nunique()

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Records", total_records)
            m2.metric("Present Count", present_count)
            m3.metric("Sessions Recorded", unique_sessions)

            st.write("")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance records logged yet for this subject.")


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    username_clean = teacher_username.strip()
    name_clean = teacher_name.strip()
    
    if not username_clean or not name_clean or not teacher_pass:
        return False, "All fields are required!"
    if check_teacher_exists(username_clean):
        return False, "Username already exists!"
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match!"
    try:
        create_teacher(username_clean, name_clean, teacher_pass)
        return True, "Successfully Created! Login Now"
    except Exception as e:
        return False, f"Registration failed: {e}"
    
    
def teacher_screen_register():
    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="large"
    )
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='registerbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Register your teacher profile")
    st.write("")
    st.write("")

    with st.form(key="teacher_register_form"):
        teacher_username = st.text_input("Enter username", placeholder="@Amitkumarprasad", key="reg_user_input")
        teacher_name = st.text_input("Enter name", placeholder="Amit kumar prasad", key="reg_name_input")
        teacher_pass = st.text_input("Enter password", placeholder="*********", type='password', key="reg_pass_input")
        teacher_pass_confirm = st.text_input("Confirm password", placeholder="*********", type='password', key="reg_conf_input")
        
        st.divider()

        submit_reg = st.form_submit_button("Register now", icon=':material/person_add:', shortcut='control+enter', use_container_width=True)

    if submit_reg:
        success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
        if success:
            st.success(message)
            time.sleep(1.5)
            st.session_state['teacher_login_type'] = 'login'
            st.rerun()
        else:
            st.error(message)

    st.write("")
    if st.button("Login Instead", icon=':material/login:', type='primary', key="login_instead_btn", use_container_width=True):
        st.session_state['teacher_login_type'] = 'login'
        st.rerun()

      
    footer_home()
