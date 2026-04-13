import streamlit as st
from groq import Groq
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Jomar AI Workspace", layout="wide", page_icon="🤖")

# --- AUTHENTICATION ---
def init_client():
    try:
        # Kinukuha ang key mula sa Streamlit Cloud Settings > Secrets
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("⚠️ API Key Error: Pakisiguradong tama ang 'GROQ_API_KEY' sa iyong Secrets.")
        st.stop()

client = init_client()

# --- STATE MANAGEMENT ---
# Dito itatabi ang usapan habang naka-open ang app
if "workspaces" not in st.session_state:
    st.session_state.workspaces = {"General": []}
if "current_workspace" not in st.session_state:
    st.session_state.current_workspace = "General"

# --- SIDEBAR: WORKSPACE SYSTEM ---
with st.sidebar:
    st.title("📁 Workspaces")
    
    # Create New Workspace
    new_ws = st.text_input("New Workspace Name:")
    if st.button("➕ Create"):
        if new_ws and new_ws not in st.session_state.workspaces:
            st.session_state.workspaces[new_ws] = []
            st.session_state.current_workspace = new_ws
            st.rerun()

    st.markdown("---")
    
    # Select Workspace
    options = list(st.session_state.workspaces.keys())
    st.session_state.current_workspace = st.selectbox(
        "Select Workspace:", 
        options, 
        index=options.index(st.session_state.current_workspace)
    )
    
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.workspaces[st.session_state.current_workspace] = []
        st.rerun()

# --- MAIN CHAT INTERFACE ---
st.title(f"🚀 Workspace: {st.session_state.current_workspace}")
st.caption("Using Llama 3.1-8B Instant via Groq Cloud")

# Display Chat History para sa napiling workspace
current_history = st.session_state.workspaces[st.session_state.current_workspace]
for chat in current_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Chat Input
if prompt := st.chat_input("Ano ang maitutulong ko sa iyo?"):
    # 1. I-save at I-display ang message ng User
    current_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Tawagin ang AI (Groq API)
    try:
        with st.chat_message("assistant"):
            # Gamitin ang Llama 3.1 (Ang model na HINDI decommissioned)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": m["role"], "content": m["content"]} for m in current_history],
                temperature=0.7,
                max_tokens=1024
            )
            
            full_response = completion.choices[0].message.content
            st.markdown(full_response)
            
        # 3. I-save ang sagot ng AI sa history
        current_history.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        if "model_decommissioned" in str(e):
            st.error("❌ Error: Ang model ay tinanggal na ni Groq. Paki-update ang code sa Llama-3.1.")
        else:
            st.error(f"❌ Error: {str(e)}")