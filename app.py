import streamlit as st
import requests
from werkzeug.security import check_password_hash
import json
import os

# -------- Configuration --------
st.set_page_config(page_title="Smart Chatbot", page_icon="💬")
st.markdown("<h1 style='text-align: center;'>💬 Smart Chatbot</h1>", unsafe_allow_html=True)

API_KEY = st.secrets["groq"]["api_key"]
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "mixtral-8x7b-32768"  # Or another valid Groq model

# -------- Dummy Users (Hash your passwords for production) --------
USERS = {
    "user@example.com": "pbkdf2:sha256:260000$4D...hashed_pass_here"
}
# Optional: allow skipping login
ALLOW_SKIP = True

# -------- Login State --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.allow_chat = False

# -------- Login Page --------
def login():
    st.subheader("🔐 Login to Smart Chatbot")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in USERS and check_password_hash(USERS[email], password):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.allow_chat = True
            st.success("✅ Logged in!")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")

    if ALLOW_SKIP:
        if st.button("Skip Login"):
            st.session_state.logged_in = True
            st.session_state.user_email = "guest"
            st.session_state.allow_chat = True
            st.warning("⚠️ Logged in as guest. Chat history won't be saved.")
            st.experimental_rerun()

# -------- Chat History File --------
def get_chat_file():
    return f"history_{st.session_state.user_email}.json"

def save_chat_history(history):
    if st.session_state.user_email != "guest":
        with open(get_chat_file(), "w") as f:
            json.dump(history, f)

def load_chat_history():
    if st.session_state.user_email != "guest":
        try:
            with open(get_chat_file(), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    return []

# -------- Groq Chat API Call --------
def get_groq_response(messages):
    res = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.7,
        },
        timeout=30
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

# -------- Chat Interface --------
def chat_interface():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history()

    # Top controls
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ New Chat"):
            st.session_state.chat_history = []
            save_chat_history([])

    with col2:
        if st.session_state.user_email != "guest":
            search = st.selectbox("📜 Chat History", [f"Chat {i+1}" for i in range(len(st.session_state.chat_history))][::-1])
    
    # Show messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    prompt = st.chat_input("Ask me anything...")
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        try:
            response = get_groq_response(st.session_state.chat_history)
            st.chat_message("assistant").markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            save_chat_history(st.session_state.chat_history)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# -------- Main App Flow --------
if not st.session_state.logged_in:
    login()
elif st.session_state.allow_chat:
    chat_interface()
