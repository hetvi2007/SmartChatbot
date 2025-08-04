import streamlit as st
import os
import json
from datetime import datetime
import requests

# === GET API KEY SECURELY ===
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)
GROQ_MODEL = "llama3-8b-8192"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# === Set Page Config ===
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖", layout="centered")

# === USER LOGIN ===
def login():
    st.session_state.logged_in = True
    st.success("✅ You are logged in!")

def skip_login():
    st.session_state.logged_in = True
    st.session_state.username = "guest"

# === MAIN CHAT FUNCTION ===
def chat_with_groq(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Error: {response.status_code} - {response.text}"

# === CHAT HISTORY SAVE ===
def save_chat(username, history):
    if not os.path.exists("history"):
        os.makedirs("history")
    with open(f"history/{username}_chat.json", "w") as f:
        json.dump(history, f)

def load_chat(username):
    try:
        with open(f"history/{username}_chat.json", "r") as f:
            return json.load(f)
    except:
        return []

# === INIT SESSION ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Login to Smart Chatbot")
    st.text_input("Enter your username", key="username_input")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Login"):
            st.session_state.username = st.session_state.username_input.strip()
            if st.session_state.username:
                login()
    with col2:
        if st.button("⏭️ Skip Login"):
            skip_login()
    st.stop()

# === CHAT UI ===
st.title("🤖 Smart Chatbot")

if "messages" not in st.session_state:
    if st.session_state.username != "guest":
        st.session_state.messages = load_chat(st.session_state.username)
    else:
        st.session_state.messages = []

# === Display Chat Messages ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === User Input ===
user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if not GROQ_API_KEY:
                st.error("❌ Missing GROQ_API_KEY in secrets.toml")
                st.stop()
            reply = chat_with_groq(st.session_state.messages)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Save history if not guest
    if st.session_state.username != "guest":
        save_chat(st.session_state.username, st.session_state.messages)
