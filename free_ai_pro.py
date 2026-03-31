import streamlit as st
from groq import Groq
import uuid
import json
import os

GROQ_API_KEY = "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"
BASE_DIR = "my_workspace"


st.set_page_config(page_title="AI Folder Tree", page_icon="🗂️", layout="wide")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def get_all_folders():
    return sorted([f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))])

def get_chats_in_folder(folder_name):
    path = os.path.join(BASE_DIR, folder_name)
    files = [f for f in os.listdir(path) if f.endswith(".json")]
    return sorted(files)

def save_json(folder, filename, data):
    path = os.path.join(BASE_DIR, folder, f"{filename}.json")
    with open(path, "w") as f:
        json.dump(data, f)

def load_json(folder, filename):
    path = os.path.join(BASE_DIR, folder, f"{filename}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

if "sel_folder" not in st.session_state:
    st.session_state.sel_folder = None
if "sel_chat_id" not in st.session_state:
    st.session_state.sel_chat_id = None

with st.sidebar:
    st.title("🗂️ AI Explorer")
    
    new_folder = st.text_input("📁 New Folder Name:", key="new_f")
    if st.button("Create Folder", use_container_width=True):
        if new_folder:
            os.makedirs(os.path.join(BASE_DIR, new_folder), exist_ok=True)
            st.rerun()

    st.markdown("---")

    folders = get_all_folders()
    if not folders:
        st.info("No folders yet. Create one above!")
    
    for folder in folders:
        with st.expander(f"📁 **{folder.upper()}**", expanded=(st.session_state.sel_folder == folder)):
            
            if st.button(f"➕ New Chat in {folder}", key=f"btn_new_{folder}", use_container_width=True):
                chat_id = str(uuid.uuid4())
                chat_count = len(get_chats_in_folder(folder)) + 1
                new_data = {"title": f"Chat {chat_count}", "messages": []}
                save_json(folder, chat_id, new_data)
                st.session_state.sel_folder = folder
                st.session_state.sel_chat_id = chat_id
                st.rerun()

            chat_files = get_chats_in_folder(folder)
            for cf in chat_files:
                cid = cf.replace(".json", "")
                cdata = load_json(folder, cid)
                
                is_active = (st.session_state.sel_chat_id == cid and st.session_state.sel_folder == folder)
                label = f"{'⭐ ' if is_active else '📄 '}{cdata['title']}"
                
                if st.button(label, key=f"chat_{folder}_{cid}", use_container_width=True):
                    st.session_state.sel_folder = folder
                    st.session_state.sel_chat_id = cid
                    st.rerun()

if st.session_state.sel_folder and st.session_state.sel_chat_id:
    current_chat = load_json(st.session_state.sel_folder, st.session_state.sel_chat_id)
    
    st.title(f"💬 {current_chat['title']}")
    st.caption(f"Path: {st.session_state.sel_folder} / {current_chat['title']}")

    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type your message..."):
        current_chat["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        try:
            client = Groq(api_key=GROQ_API_KEY)
            with st.chat_message("assistant"):
                box = st.empty()
                full_text = ""
                history = [{"role": "system", "content": "You are a helpful assistant."}] + current_chat["messages"]
                
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history,
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_text += content
                        box.markdown(full_text + "▌")
                box.markdown(full_text)

            current_chat["messages"].append({"role": "assistant", "content": full_text})
            save_json(st.session_state.sel_folder, st.session_state.sel_chat_id, current_chat)
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.title("My Personal AI Workspace")
    st.write("👈 In the right sidebar, select a folder to view its chats.")