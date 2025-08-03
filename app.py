import streamlit as st
import requests
from datetime import datetime
import os

# Load API key
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ----- LOGIN -----
def login():
    st.subheader("🔐 Login to Smart Chatbot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    login_clicked = col1.button("Login")
    skip_clicked = col2.button("Skip Login")

    if login_clicked and username and password:
        st.session_state["logged_in"] = True
        st.success(f"Welcome, {username} 👋")
    elif skip_clicked:
        st.session_state["logged_in"] = True
        st.warning("You skipped login!")

# ----- INIT -----
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "search_term" not in st.session_state:
    st.session_state["search_term"] = ""

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ----- HEADER -----
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖")
st.title("🤖 Smart Chatbot")

# ----- SEARCH -----
with st.sidebar:
    st.subheader("🔍 Search Chat")
    search_input = st.text_input("Search keyword")
    if search_input:
        st.session_state.search_term = search_input.lower()
    if st.button("🔄 Clear Search"):
        st.session_state.search_term = ""

# ----- CHAT HISTORY DISPLAY -----
for msg in st.session_state.messages:
    content_lower = msg["content"].lower()
    if not st.session_state.search_term or st.session_state.search_term in content_lower:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ----- CHAT INPUT -----
user_input = st.chat_input("Ask anything...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",  # You can change model here
                "messages": [{"role": "system", "content": "You are a smart helpful assistant."}] + st.session_state.messages,
                "temperature": 0.7
            },
        )

        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        st.chat_message("assistant").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# ----- EXPORT CHAT -----
def export_chat():
    chat_file = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(chat_file, "w", encoding="utf-8") as f:
        for msg in st.session_state.messages:
            role = msg["role"].capitalize()
            f.write(f"{role}: {msg['content']}\n\n")
    return chat_file

st.sidebar.markdown("---")
if st.sidebar.button("💾 Export Chat"):
    file_path = export_chat()
    st.sidebar.success("Chat exported!")
    with open(file_path, "rb") as f:
        st.sidebar.download_button("⬇️ Download Chat", data=f, file_name=file_path)

