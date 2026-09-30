import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time

@st.dialog("Enroll in Subject")
def enroll_dialog(student_id=None):
    if not student_id:
        student = st.session_state.get('student_data') or st.session_state.get('student_user', {})
        student_id = student.get('student_id') or student.get('id')
    
    st.write("Enter the subject code provided by your teacher to enroll")
    join_code = st.text_input('Subject Code', placeholder='E.g. CS101')

    if st.button('Enroll now', type='primary', use_container_width=True):
        if join_code:
            res = supabase.table('subjects').select('subject_id,name,subject_code').ilike('subject_code', join_code.strip()).execute()
            
            if res.data:
                subject = res.data[0]
                target_sub_id = subject['subject_id']
                
                check = supabase.table('subject_students').select('*').eq('subject_id', target_sub_id).eq('student_id', student_id).execute()
                if check.data:
                    st.warning('You are already enrolled in this course')
                else:
                    enroll_student_to_subject(student_id, target_sub_id)
                    st.success(f"Successfully enrolled in {subject.get('name', 'the subject')}")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error('Invalid Subject Code')
        else:
            st.warning('Please enter subject code')