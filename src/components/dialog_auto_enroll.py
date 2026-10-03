import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time

@st.dialog("Quick Enrollment")
def dialog_auto_enroll(subject_code):
    student = st.session_state.get('student_data') or st.session_state.get('student_user', {})
    student_id = student.get('student_id') or student.get('id')

    if not student_id:
        return

    res = supabase.table('subjects').select('subject_id,name,subject_code').ilike('subject_code', subject_code.strip()).execute()
    if not res.data:
        st.error(f'Subject Code "{subject_code}" not found!')
        if st.button('Close', use_container_width=True):
            st.query_params.pop('join_code', None)
            st.query_params.pop('join-code', None)
            st.rerun()
        return

    subject = res.data[0]
    target_sub_id = subject['subject_id']

    check = supabase.table('subject_students').select('*').eq('subject_id', target_sub_id).eq('student_id', student_id).execute()
    if check.data:
        st.info(f"You are already enrolled in **{subject.get('name', 'this course')}**!")
        if st.button('Close', use_container_width=True):
            st.query_params.pop('join_code', None)
            st.query_params.pop('join-code', None)
            st.rerun()
        return

    st.markdown(f"Would you like to enroll in **{subject.get('name', 'this course')}** (`{subject.get('subject_code', subject_code)}`)?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button('No thanks', use_container_width=True):
            st.query_params.pop('join_code', None)
            st.query_params.pop('join-code', None)
            st.rerun()
    with col2:
        if st.button('Yes, Enroll now', type='primary', use_container_width=True):
            enroll_student_to_subject(student_id, target_sub_id)
            st.success(f"Enrolled successfully in {subject.get('name', 'course')}!")
            st.query_params.pop('join_code', None)
            st.query_params.pop('join-code', None)
            time.sleep(0.5)
            st.rerun()

    st.divider()


                        
                        
                
                
