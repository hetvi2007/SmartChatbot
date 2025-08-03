import streamlit as st
import requests
import json
from werkzeug.security import check_password_hash
from datetime import datetime
import os

# -------------------------------
# 🔐 User login credentials
USERS = {
    "user@example.com": "pbkdf2:sha256:260000$abc$your_hashed_password_here"
}
ALLOW_SKIP = True  # allow skip login

# -------------------------------
# 🔑 API & Settings
GROQ_API_KEY = st.secrets["groq"]["api_key"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "mixtral-8x7b-32768"

# -------------------------------
# 📁 Setup folders
if not os.path.exists("chats"):
    os.makedirs("chats")

# -------------------------------
# 💬 App UI
st.set_page_config(page_title="Smart Chatbot", page_icon="💬")
st.title("💬 Smart Chatbot")

# -------------------------------
# 👤 Login system
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
            st.stop()
        else:
            st.error("Invalid email or password.")

    if ALLOW_SKIP:
        if st.button("Skip Login"):
            st.session_state.logged_in = True
            st.session_state.user_email = "guest"
            st.session_state.allow_chat = True
            st.warning("⚠️ Logged in as guest. Chat history won't be saved.")
            st.stop()

# -------------------------------
# 🧠 Chat function
def chat_with_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": MODEL,
        "messages": messages
    }

    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        res.raise_for_status()
        reply = res.json()["choices"][0]["message"]["content"]
        return reply
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return None

# -------------------------------
# 💾 Save chat history
def save_chat(user_email, messages):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"chats/{user_email}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(messages, f, indent=2)

# -------------------------------
# 🧠 Main App
if "logged_in" not in st.session_state:
    login()

if st.session_state.get("allow_chat"):
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # Chat history selection
    st.sidebar.button("➕ New Chat", on_click=lambda: st.session_state.pop("messages", None))
    if st.session_state.user_email != "guest":
        history_files = [f for f in os.listdir("chats") if f.startswith(st.session_state.user_email)]
        selected_history = st.sidebar.selectbox("📜 Chat History", [""] + history_files)
        if selected_history:
            with open(os.path.join("chats", selected_history), "r") as f:
                st.session_state.messages = json.load(f)

    # Display chat
    for msg in st.session_state.messages[1:]:  # skip system
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask me anything...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = chat_with_groq(st.session_state.messages)
        if reply:
            st.chat_message("assistant").markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            if st.session_state.user_email != "guest":
                save_chat(st.session_state.user_email, st.session_state.messages)
