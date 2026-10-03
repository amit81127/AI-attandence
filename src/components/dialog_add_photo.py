import streamlit as st
from PIL import Image
import time

@st.dialog("Capture or Upload Photos")
def add_photo_dialog():
    st.write('Add classroom photos to scan for attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = 'primary' if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button('📷 Camera', type=type_camera, use_container_width=True):
            st.session_state.photo_tab = 'camera'
            st.rerun()
    with t2:
        type_upload = 'primary' if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button('📁 Upload Photos', type=type_upload, use_container_width=True):
            st.session_state.photo_tab = 'upload'
            st.rerun()

    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input('Take Snapshot', key='dialog_cam')
        if cam_photo:
            img = Image.open(cam_photo)
            st.session_state.attendance_images.append(img)
            st.toast('Photo Captured!', icon='📸')
            time.sleep(0.3)
            st.rerun()

    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader(
            'Upload Classroom Photos',
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg'],
            key='dialog_upload'
        )
        if uploaded_files:
            if st.button('Add Uploaded Photos', type='primary', use_container_width=True):
                for f in uploaded_files:
                    st.session_state.attendance_images.append(Image.open(f))
                st.toast(f'{len(uploaded_files)} photo(s) added!', icon='✅')
                time.sleep(0.3)
                st.rerun()
        
    if st.session_state.attendance_images:
        st.info(f"Total photos ready for scanning: **{len(st.session_state.attendance_images)}**")

    st.divider()
    if st.button('Done', type='primary', use_container_width=True):
        st.rerun()

