import streamlit as st
import requests
import os
import json
from datetime import datetime
from werkzeug.security import check_password_hash

# PAGE CONFIG
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖")

# Load users from file
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ---------------------
# SESSION STATE INIT
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# API key from secrets
GROQ_API_KEY = st.secrets["groq"]["api_key"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "mixtral-8x7b-32768"

# 📁 Ensure history folder exists
os.makedirs("chat_history", exist_ok=True)

# ---------------------------
# LOGIN PAGE
# ---------------------------
def login():
    st.title("🔐 Login to Smart Chatbot")
    users = load_users()

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in users and check_password_hash(users[email], password):
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")

# ---------------------------
# SAVE CHAT
# ---------------------------
def save_chat():
    filename = f"chat_history/{st.session_state.email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(st.session_state.messages, f)

# ---------------------------
# SEARCH CHAT
# ---------------------------
def search_chats(keyword):
    results = []
    for fname in os.listdir("chat_history"):
        if fname.startswith(st.session_state.email):
            with open(os.path.join("chat_history", fname), "r") as f:
                chat = json.load(f)
                for msg in chat:
                    if keyword.lower() in msg["content"].lower():
                        results.append((fname, msg["content"]))
    return results

# ---------------------------
# MAIN CHATBOT UI
# ---------------------------
def chatbot_ui():
    st.title("💬 Smart Python Chatbot")
    st.markdown(f"👤 **User:** {st.session_state.email}")

    with st.expander("🔍 Search Past Chats"):
        keyword = st.text_input("Search keyword")
        if keyword:
            matches = search_chats(keyword)
            for fname, line in matches:
                st.markdown(f"📁 **{fname}**: {line}")

    if st.button("🆕 New Chat"):
        save_chat()
        st.session_state.messages = []
        st.experimental_rerun()

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    user_input = st.chat_input("Say something...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": st.session_state.messages,
                }
            )
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                st.chat_message("assistant").markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(f"⚠️ API Error: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# ---------------------------
# APP RUN
# ---------------------------
if st.session_state.logged_in:
    chatbot_ui()
else:
    login()
