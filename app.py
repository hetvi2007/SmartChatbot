import streamlit as st
import os
import json
import requests
from werkzeug.security import check_password_hash

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Smart Chatbot", page_icon="💬", layout="centered")

# Your Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY") or "gsk_xxx_your_real_key_here"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "mixtral-8x7b-32768"

# Simple users database
USERS = {
    "test@example.com": {
        "password_hash": "pbkdf2:sha256:260000$TestKey$1a77d49f25cb5e...",  # Replace with real hashed password
        "name": "Test User"
    }
}

# -------------------- AUTH --------------------
def login():
    st.title("🔐 Login to Smart Chatbot")

    if "skip_login" in st.session_state and st.session_state.skip_login:
        st.info("⚠️ Logged in as guest. Chat history won't be saved.")
        return

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login"):
            user = USERS.get(email)
            if user and check_password_hash(user["password_hash"], password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error("Invalid email or password.")
    with col2:
        if st.button("Skip Login"):
            st.session_state.skip_login = True
            st.rerun()

# -------------------- RESET --------------------
def reset_login():
    if st.sidebar.button("🔁 Reset Login"):
        for key in ["logged_in", "skip_login", "email"]:
            st.session_state.pop(key, None)
        st.rerun()

# -------------------- GROQ CHAT --------------------
def ask_groq(prompt, history):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": history + [{"role": "user", "content": prompt}]
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        st.error(f"⚠️ Error: {response.status_code} - {response.text}")
        return None

# -------------------- UI --------------------
def main_ui():
    st.title("💬 Smart Chatbot")

    reset_login()  # Sidebar reset button

    # Load chat history from session or storage
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar history
    with st.sidebar:
        st.button("➕ New Chat", on_click=lambda: st.session_state.update({"messages": []}))
        if "email" in st.session_state:
            st.markdown("### 📜 Chat History")
            # Placeholder for future file-based history

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    prompt = st.chat_input("Ask me anything…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = ask_groq(prompt, st.session_state.messages[:-1])
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

# -------------------- RUN APP --------------------
if "logged_in" not in st.session_state and "skip_login" not in st.session_state:
    login()
else:
    main_ui()
