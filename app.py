import streamlit as st
import os, json, uuid
from datetime import datetime
from werkzeug.security import check_password_hash
import requests

# API config
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = st.secrets["groq"]["api_key"]

# App config
st.set_page_config(page_title="Smart Chatbot", page_icon="💬")

# Load user data
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

# Save chat
def save_chat(email, message):
    os.makedirs("chat_history", exist_ok=True)
    user_file = os.path.join("chat_history", f"{email}.json")
    data = []
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
    data.append(message)
    with open(user_file, "w") as f:
        json.dump(data, f, indent=2)

# Load chat
def load_chat(email):
    user_file = os.path.join("chat_history", f"{email}.json")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            return json.load(f)
    return []

# Login form
def login():
    st.header("🔐 Login to Smart Chatbot")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        user = users.get(email)
        if user and check_password_hash(user["password"], password):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.success("Login successful!")
        else:
            st.error("Invalid email or password.")
    if st.button("Continue without login"):
        st.session_state.authenticated = True
        st.session_state.user_email = f"guest_{uuid.uuid4().hex}"

# Chat UI
def chat_ui():
    st.title("💬 Your Smart Python Chatbot")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.expander("📜 Chat History", expanded=False):
        chats = load_chat(st.session_state.user_email)
        for chat in chats[-5:]:
            st.markdown(f"**{chat['role'].capitalize()}**: {chat['content']}")

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    prompt = st.chat_input("Ask me anything...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            res = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": st.session_state.messages,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            res.raise_for_status()
            reply = res.json()["choices"][0]["message"]["content"]
            st.chat_message("assistant").write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            save_chat(st.session_state.user_email, {"role": "user", "content": prompt})
            save_chat(st.session_state.user_email, {"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# Run app
if "authenticated" not in st.session_state:
    login()
elif st.session_state.authenticated:
    chat_ui()
