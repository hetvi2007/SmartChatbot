import streamlit as st
import requests
import base64
from datetime import datetime
from werkzeug.security import check_password_hash
import os

# ========================
# 🔐 Login System (Optional)
# ========================
def login():
    if st.session_state.get("logged_in"):
        return True

    st.title("🔐 Login to SmartChatbot")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            valid_user = st.secrets["credentials"]["username"]
            valid_hash = st.secrets["credentials"]["password_hash"]

            if username == valid_user and check_password_hash(valid_hash, password):
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid username or password")

    st.stop()

if "skip_login" not in st.session_state:
    if st.sidebar.button("🚪 Skip Login"):
        st.session_state["logged_in"] = True
        st.session_state["skip_login"] = True

if not st.session_state.get("logged_in"):
    login()

# ========================
# 🌙 Theme Switcher
# ========================
theme = st.sidebar.selectbox("🌈 Choose Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""<style>body { background-color: #111; color: #eee; }</style>""", unsafe_allow_html=True)

# ========================
# 🌍 App Config & Setup
# ========================
st.set_page_config(page_title="Smart Chatbot", layout="wide")
st.title("🤖 SmartChatbot + 🖼️ Image + 📎 Upload + 💾 Save Chat")

# Groq & Stability
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image"

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# Display chat history
for msg in st.session_state.messages[1:]:  # skip system prompt
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========================
# 🔍 Image Detection
# ========================
def is_image_prompt(text):
    keywords = ["draw", "generate image", "show me", "picture of", "create image", "visualize"]
    return any(k in text.lower() for k in keywords)

# ========================
# 🎨 Image Generator
# ========================
def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }
    response = requests.post(STABILITY_API_URL, headers=headers, json=json_data)

    if response.status_code == 200:
        img_base64 = response.json()["artifacts"][0]["base64"]
        return img_base64
    else:
        st.error("❌ Image generation failed.")
        return None

# ========================
# 📎 File Upload
# ========================
uploaded_files = st.sidebar.file_uploader("📁 Upload files", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        st.sidebar.success(f"Uploaded: {file.name}")

# ========================
# 💬 Chat Input
# ========================
user_prompt = st.chat_input("Type your message here...")

if user_prompt:
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Image prompt
    if is_image_prompt(user_prompt):
        with st.chat_message("assistant"):
            st.markdown("🖼 Generating image...")
            image_data = generate_image(user_prompt)
            if image_data:
                st.image(base
