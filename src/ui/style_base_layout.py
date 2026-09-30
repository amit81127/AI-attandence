import streamlit as st

def style_background_home():
     st.markdown("""
         <style>
            .stApp{
              background:#5865f2 !important;
            }
            .stApp div[data-testid="stColumn"]{
               background-color:#E0E3FF !important;
               border-radius: 5rem !important;
               padding:2.5rem !important;

            }
         </style>
               
               """,unsafe_allow_html=True)


def style_background_dashboard():
     st.markdown("""
         <style>
            .stApp{
              background:#E0E3ff !important;
            }
         </style>
               
               """,unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

        /* #MainMenu, footer, header {
            visibility: hidden;
        } */

        .block-container {
            padding-top: 1.5rem !important;
        }

        h1, h2 {
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 2rem !important;
            line-height: 0.9 !important;
            margin-bottom: 0rem !important;
        }

        h3, h4, p {
            font-family: 'Outfit', sans-serif !important;
        }

        div.stButton > button {
            background: #E865F2 !important;
            color: white !important;
            border-radius: 1.5rem !important;
            border: none !important;
            padding: 10px 20px !important;
            transition: transform 0.25s ease-in-out !important;
        }

        div.stButton > button:hover {
            transform: scale(1.05) !important;
        }
         .stButton > button[kind="primary"] {
            background-color: #000000 !important;
            color: white !important;
            border: none !important;
        }

        .stButton > button[kind="secondary"] {
            background-color: #e785ff !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)