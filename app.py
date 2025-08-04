import streamlit as st
import requests
import os
from datetime import datetime
from werkzeug.security import check_password_hash

# ==== SETUP ====

st.set_page_config(page_title="Smart Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Smart Chatbot")

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_MODEL = "llama3-8b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ==== AUTH ====

def login():
    st.session_state.authenticated = False

    with st.form("Login"):
        st.subheader("🔐 Login to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns([1, 1])
        with col1:
            login_btn = st.form_submit_button("Login")
        with col2:
            skip_btn = st.form_submit_button("Skip Login")

        if login_btn:
            valid_username = st.secrets["credentials"]["username"]
            valid_pw_hash = st.secrets["credentials"]["password_hash"]

            if username == valid_username and check_password_hash(valid_pw_hash, password):
                st.session_state.authenticated = True
                st.success("✅ Logged in!")
            else:
                st.error("❌ Invalid username or password.")
        elif skip_btn:
            st.session_state.authenticated = True
            st.info("⚠️ You skipped login. Some features may be limited.")

if "authenticated" not in st.session_state:
    login()

if not st.session_state.authenticated:
    st.stop()

# ==== CHAT INITIALIZE ====

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==== CHAT UI ====

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a smart assistant."}
                    ] + st.session_state.messages
                },
                timeout=20
            )

            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                st.chat_message("assistant").markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(f"⚠️ Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"⚠️ Failed to connect: {str(e)}")

# ==== TOOLBAR ====

with st.sidebar:
    st.markdown("## ⚙️ Options")
    if st.button("🧹 New Chat"):
        st.session_state.messages = []
        st.experimental_rerun()
    if st.button("🚪 Logout"):
        del st.session_state["authenticated"]
        st.experimental_rerun()
    st.markdown("---")
    st.caption("Built with ❤️ using GROQ + Streamlit")
