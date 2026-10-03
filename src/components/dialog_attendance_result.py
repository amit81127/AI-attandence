import streamlit as st
import time
from src.database.db import create_attendance


def show_attendance_result(df, logs):
    st.write("Please review attendance before confirming:")
    if df is not None and not df.empty:
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("No attendance records to display.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()
    with col2:
        if st.button("Confirm Attendance", type='primary', use_container_width=True):
            try:
                if logs:
                    create_attendance(logs)
                st.toast("Attendance confirmed!", icon='✅')
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Sync failed: {e}")


@st.dialog("Attendance Results")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)