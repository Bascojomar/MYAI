import streamlit as st
from groq import Groq
import uuid
import json
import os

GROQ_API_KEY = "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"
DATA_FILE = "chat_data.json"

st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="wide")

# --- FUNCTIONS PARA SA PAG-SAVE AT LOAD ---
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

# --- INITIALIZE CHATS FROM FILE OR SESSION ---
if "all_chats" not in st.session_state:
    saved_data = load_data()
    if saved_data:
        st.session_state.all_chats = saved_data["all_chats"]
        st.session_state.current_chat_id = saved_data["current_chat_id"]
    else:
        # Default kung walang saved file
        first_id = str(uuid.uuid4())
        st.session_state.all_chats = {
            first_id: {"title": "Chat 1", "messages": []}
        }
        st.session_state.current_chat_id = first_id

# --- SIDEBAR ---
with st.sidebar:
    st.title("My Chats 💬")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        chat_count = len(st.session_state.all_chats) + 1
        st.session_state.all_chats[new_id] = {
            "title": f"Chat {chat_count}",
            "messages": []
        }
        st.session_state.current_chat_id = new_id
        save_data({"all_chats": st.session_state.all_chats, "current_chat_id": st.session_state.current_chat_id})
        st.rerun()

    st.markdown("---")
    for chat_id, chat_data in st.session_state.all_chats.items():
        is_current = (chat_id == st.session_state.current_chat_id)
        if st.button(f"{'🟢 ' if is_current else ''}{chat_data['title']}", key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            save_data({"all_chats": st.session_state.all_chats, "current_chat_id": st.session_state.current_chat_id})
            st.rerun()

    if st.button("🗑️ Delete All History"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.session_state.clear()
        st.rerun()

# --- MAIN CHAT ---
current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
st.title(f"💬 {current_chat['title']}")

for message in current_chat["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Type here..."):
    current_chat["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        client = Groq(api_key=GROQ_API_KEY)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            # Dagdagan ng system message para sa AI behavior
            msgs_to_send = [{"role": "system", "content": "You are a helpful assistant."}] + current_chat["messages"]
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs_to_send,
                stream=True
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        current_chat["messages"].append({"role": "assistant", "content": full_response})
        # I-SAVE PAGKATAPOS NG REPLY
        save_data({"all_chats": st.session_state.all_chats, "current_chat_id": st.session_state.current_chat_id})

    except Exception as e:
        st.error(f"Error: {str(e)}")