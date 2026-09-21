import streamlit as st

def footer_home():
    st.markdown("""
    <style>
        .footer-credit {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            color: black;
            font-size: 14px;
            border-top: 1px solid rgba(255,255,255,0.15);
        }

        .footer-name {
            color: white;
            font-weight: 700;

        }
    </style>

    <div class="footer-credit">
        Made by <span class="footer-name">Amit Kumar</span>
    </div>
    """, unsafe_allow_html=True)