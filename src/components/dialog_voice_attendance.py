import streamlit as st
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_result import show_attendance_result


@st.dialog('Voice Attendance')
def voice_attendance_dialog(selected_subject_id):
    st.write('Record audio of students saying "Present"')

    audio_data = st.audio_input("Record classroom audio")

    if st.button('Analyze Audio', use_container_width=True, type='primary'):
        if not audio_data:
            st.warning("Please record audio before analyzing.")
            return

        with st.spinner('Processing Audio... please wait'):
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
                return

            candidates_dict = {}
            for s in enrolled_students:
                student_info = s.get('students')
                if student_info:
                    sid = student_info.get('student_id') or student_info.get('id')
                    voice_emb = student_info.get('voice_embedding')
                    if sid and voice_emb:
                        candidates_dict[sid] = voice_emb

            if not candidates_dict:
                st.error("No enrolled students have voice embeddings registered.")
                return

            audio_bytes = audio_data.getvalue() if hasattr(audio_data, 'getvalue') else audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict) or {}

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for node in enrolled_students:
                student = node.get('students')
                if not student:
                    continue
                sid = student.get('student_id') or student.get('id')
                score = detected_scores.get(sid, 0.0)
                is_present = bool(score >= 0.2)

                results.append({
                    "Name": student.get('name', 'Unknown'),
                    "ID": sid,
                    "Score": f"{score:.2f}" if is_present else "-",
                    "Status": "Present" if is_present else "Absent"
                })
                attendance_to_log.append({
                    'student_id': sid,
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)