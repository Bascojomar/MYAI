import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Chat Pro - Permanent", layout="wide")

SHEET_ID = "ILAGAY_DITO_ANG_SHEET_ID_MO" 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except:
        return pd.DataFrame(columns=["folder_name", "role", "content", "timestamp"])
if "folders" not in st.session_state:
    st.session_state.folders = {}

st.sidebar.title("📁 Workspaces")
new_f = st.sidebar.text_input("New Folder:")
if st.sidebar.button("Create") and new_f:
    st.session_state.folders[new_f] = []

selected = st.sidebar.selectbox("Select:", ["---"] + list(st.session_state.folders.keys()))

st.title("🤖 AI Workspace")

if selected != "---":
    for chat in st.session_state.folders[selected]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if prompt := st.chat_input("Chat here..."):
        st.session_state.folders[selected].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        res = completion.choices[0].message.content
        st.session_state.folders[selected].append({"role": "assistant", "content": res})
        with st.chat_message("assistant"):
            st.markdown(res)
else:
    st.info("Pumili ng folder.")