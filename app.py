import streamlit as st
import requests
import json
import os

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Smart Chatbot", page_icon="💬", layout="wide")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "your_groq_api_key_here"  # Replace or use secrets
MODEL = "llama3-8b-8192"

# ------------------ SESSION INIT ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "skip_login" not in st.session_state:
    st.session_state.skip_login = False

if "email" not in st.session_state:
    st.session_state.email = None

if "history" not in st.session_state:
    st.session_state.history = {}

# ------------------ LOGIN ------------------
def login():
    st.title("🔐 Login to Smart Chatbot")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login"):
            if email == "admin@email.com" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")

    with col2:
        if st.button("Skip Login", type="secondary"):
            st.session_state.skip_login = True
            st.warning("⚠️ Logged in as guest. Chat history won't be saved.")
            st.rerun()

# ------------------ GROQ API ------------------
def ask_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

# ------------------ CHAT UI ------------------
def chat_interface():
    st.title("💬 Smart Chatbot")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("➕ New Chat"):
            st.session_state.messages = []

    if st.session_state.logged_in:
        with col1:
            if st.session_state.history:
                selected = st.selectbox("📜 Chat History", list(st.session_state.history.keys()))
                if selected:
                    st.session_state.messages = st.session_state.history[selected]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask me anything...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                reply = ask_groq(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                # Save chat
                if st.session_state.logged_in and st.session_state.email:
                    chat_id = f"{st.session_state.email}_chat_{len(st.session_state.history)+1}"
                    st.session_state.history[chat_id] = st.session_state.messages.copy()
            except Exception as e:
                st.error(str(e))

# ------------------ MAIN ------------------
def main():
    if not st.session_state.logged_in and not st.session_state.skip_login:
        login()
    else:
        chat_interface()

main()
