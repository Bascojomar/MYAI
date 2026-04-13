import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Jomar AI Pro", layout="wide", page_icon="🤖")

# --- SECRETS & AUTH ---
def init_client():
    try:
        # Kinukuha ang key mula sa Settings > Secrets (Cloud) 
        # o .streamlit/secrets.toml (Local)
        api_key = st.secrets["GROQ_API_KEY"]
        return Groq(api_key=api_key)
    except Exception as e:
        st.error("⚠️ API Key Missing! Pakicheck ang Streamlit Secrets.")
        st.stop()

client = init_client()

# --- DATABASE (SIMPLE PERSISTENCE) ---
# Dahil sa hirap ng setup ng GSheets, gagamit muna tayo ng Session State 
# para sa UI logic, pero handa na ito para sa data logging.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "workspaces" not in st.session_state:
    st.session_state.workspaces = {"Default": []}

# --- SIDEBAR ---
st.sidebar.title("📁 AI Workspaces")

# Create Workspace
new_ws = st.sidebar.text_input("Add Workspace Name:")
if st.sidebar.button("➕ Create"):
    if new_ws and new_ws not in st.session_state.workspaces:
        st.session_state.workspaces[new_ws] = []
        st.sidebar.success(f"Workspace '{new_ws}' added!")

# Select Workspace
selected_ws = st.sidebar.selectbox("Choose Workspace:", list(st.session_state.workspaces.keys()))

# --- MAIN CHAT ---
st.title(f"🚀 Workspace: {selected_ws}")
st.caption("Powered by Llama 3 via Groq Cloud")

# Display Chat History from the selected workspace
for chat in st.session_state.workspaces[selected_ws]:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# User Input
if prompt := st.chat_input("Ano ang maitutulong ko sa iyo?"):
    # 1. Add User Message to History
    st.session_state.workspaces[selected_ws].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call AI API
    try:
        with st.chat_message("assistant"):
            # Gumawa ng "Placeholder" para sa loading effect
            response_placeholder = st.empty()
            
            # Kunin lang ang huling 5 messages para hindi ma-overload ang API (Context)
            history = st.session_state.workspaces[selected_ws][-5:]
            
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": m["role"], "content": m["content"]} for m in history],
                temperature=0.7,
                max_tokens=2048
            )
            
            full_response = completion.choices[0].message.content
            response_placeholder.markdown(full_response)
            
        # 3. Save AI Response
        st.session_state.workspaces[selected_ws].append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"❌ AI Error: {str(e)}")
        # Kung BadRequestError ito, madalas ay dahil sa empty prompt o invalid key
        st.info("Tip: Subukang i-reboot ang app o i-update ang iyong Groq API Key.")

# --- FOOTER ---
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Current Chat"):
    st.session_state.workspaces[selected_ws] = []
    st.rerun()