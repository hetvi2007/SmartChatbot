import streamlit as st
import requests
import os
import base64
from datetime import datetime
from werkzeug.security import check_password_hash
from io import BytesIO

# ----------------- LOGIN SYSTEM -----------------
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if username and password:
        if username == st.secrets["credentials"]["username"] and \
           check_password_hash(st.secrets["credentials"]["password_hash"], password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid username or password")
            return False
    return False


# ----------------- CHATBOT SETTINGS -----------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="🤖 Smart Chatbot", layout="wide")

# Apply theme
theme_mode = st.radio("Theme mode:", ["Light", "Dark"])
if theme_mode == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #1E1E1E; color: white; }
        </style>
        """, unsafe_allow_html=True
    )

# ----------------- MAIN APP -----------------
if check_login():

    st.title("🤖 Smart Chatbot with Image Generation")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat input
    user_input = st.text_input("Ask something:")

    if st.button("Send") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": st.session_state.messages
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            bot_reply = response.json()["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            st.error("API request failed")

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

    # Save & download chat history
    if st.button("Download Chat History"):
        chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        b64 = base64.b64encode(chat_text.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">📥 Download Chat</a>'
        st.markdown(href, unsafe_allow_html=True)

    # ----------------- IMAGE GENERATION -----------------
    st.subheader("🎨 Generate an Image")
    image_prompt = st.text_input("Describe the image you want to generate:")

    if st.button("Generate Image") and image_prompt:
        img_api_url = "https://api.groq.com/openai/v1/images/generations"
        img_payload = {
            "model": "gpt-image-1",
            "prompt": image_prompt,
            "size": "512x512"
        }
        img_headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

        img_response = requests.post(img_api_url, json=img_payload, headers=img_headers)

        if img_response.status_code == 200:
            img_url = img_response.json()["data"][0]["url"]
            st.image(img_url, caption=image_prompt)
        else:
            st.error("Image generation failed")

    # ----------------- FILE UPLOAD -----------------
    st.subheader("📂 Upload a File")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file:
        st.success(f"Uploaded file: {uploaded_file.name}")
