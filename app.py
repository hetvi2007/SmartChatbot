import streamlit as st
import requests
import os
import json
from datetime import datetime

# PAGE CONFIG
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖", layout="centered")

# ✅ Secrets
GROQ_API_KEY = st.secrets["groq"]["api_key"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "mixtral-8x7b-32768"

# 📁 Ensure history folder exists
os.makedirs("chat_history", exist_ok=True)

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# LOGIN PAGE
# ---------------------------
def login():
    st.title("🔐 Login to Smart Chatbot")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email and password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success("✅ Logged in!")
            st.experimental_rerun()
        else:
            st.error("Please enter email and password.")

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
    st.markdown("You are chatting as: **" + st.session_state.email + "**")

    # Search
    with st.expander("🔍 Search Past Chats"):
        keyword = st.text_input("Search keyword")
        if keyword:
            matches = search_chats(keyword)
            for fname, line in matches:
                st.markdown(f"📁 **{fname}**: {line}")

    # New Chat
    if st.button("🆕 New Chat"):
        save_chat()
        st.session_state.messages = []
        st.experimental_rerun()

    # Display past messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # User input
    user_input = st.chat_input("Say something...")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Groq API call
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
                st.error("⚠️ API Error: " + response.text)

        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")

# ---------------------------
# APP START
# ---------------------------
if st.session_state.logged_in:
    chatbot_ui()
else:
    login()
