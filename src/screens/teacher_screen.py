import streamlit as st
from src.ui.style_base_layout import style_background_dashboard, style_base_layout
from src.components.footer import footer_home
from src.components.header import header_dashboard

from src.database.db import check_teacher_exists,create_teacher,teacher_login

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
                st.session_state['teacher_user'] = teacher
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
    teacher = st.session_state.get('teacher_user', {})
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
        if st.button("Logout",type='secondary',key='loginbackbtn',shortcut='control+backspace'):
            st.session_state['is_logged_in']=False
            del st.session_state.teacher_data
            st.rerun()
           

    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab='take_attendence'
    tab1,tab2,tab3=st.columns(3)

    with tab1:
        type1="primary" if st.session_state.current_teacher_tab=='take_attendence' else "tertiary"
        if st.button("Take Attandence",width='stretch',type=type1,icon=':material/ar_on_you:'):
           st.session_state.current_teacher_tab='take_attendence'
           st.rerun()
    
    with tab2:
        type2="primary" if st.session_state.current_teacher_tab=='manage_subjects' else "tertiary"
        if st.button("Manage Subjects",width='stretch',type=type2,icon=':material/book_ribbon:'):
           st.session_state.current_teacher_tab='manage_subjects'
           st.rerun()
           
    with tab3:
        type3="primary" if st.session_state.current_teacher_tab=='attendence_records' else "tertiary"
        if st.button("Attendence Records",width='stretch',type=type3,icon=':material/cards_stack:'):
           st.session_state.current_teacher_tab='attendence_records'
           st.rerun()

    st.divider()
    
    if st.session_state.current_teacher_tab=='take_attendence':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab=='manage_subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab=='attendence_records':
        teacher_tab_attendance_records()
        

    footer_home()


def teacher_tab_take_attendance():
    st.subheader("Take Attendance")

def teacher_tab_manage_subjects():
    st.subheader("Manage Subjects")

def teacher_tab_attendance_records():
    st.subheader("Attendance Records")

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
            import time
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







