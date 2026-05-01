import streamlit as st

def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/snapclass-logo.png"
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px;">
            <img src='{logo_url}' style='height:100px;' />
            <h1 style='text-align:center; color:#E0E3FF; font-family: "Inter", sans-serif;'>ATTEND<br>AI</h1>
        </div>
        """, unsafe_allow_html=True)

def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/snapclass-logo.png"
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:10px; margin-top:30px;">
            <img src='{logo_url}' style='height:85px;' />
            <h2 style='text-align:left; color:#5865F2; font-family: "Inter", sans-serif;'>ATTEND<br>AI</h2>
        </div>
        """, unsafe_allow_html=True)