import streamlit as st
from groq import Groq
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Jomar AI Workspace", layout="wide", page_icon="🤖")

# --- AUTHENTICATION ---
def init_client():
    try:
        # Retrieves key from Streamlit Cloud Settings > Secrets
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error("⚠️ API Key Error: Please ensure 'GROQ_API_KEY' is correctly set in your Secrets.")
        st.stop()

client = init_client()

# --- STATE MANAGEMENT ---
# Stores chats during the active session
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

# Display Chat History for the selected workspace
current_history = st.session_state.workspaces[st.session_state.current_workspace]
for chat in current_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Chat Input
if prompt := st.chat_input("How can I help you today?"):
    # 1. Save and Display User message
    current_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the AI (Groq API)
    try:
        with st.chat_message("assistant"):
            # Using Llama 3.1 (The active, supported model)
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": m["role"], "content": m["content"]} for m in current_history],
                temperature=0.7,
                max_tokens=1024
            )
            
            full_response = completion.choices[0].message.content
            st.markdown(full_response)
            
        # 3. Save AI response to history
        current_history.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        if "model_decommissioned" in str(e):
            st.error("❌ Error: The model was decommissioned by Groq. Please update the code to Llama-3.1.")
        else:
            st.error(f"❌ Error: {str(e)}")