import streamlit as st
import requests
import base64
from datetime import datetime

# ===== PAGE CONFIG =====
st.set_page_config(page_title="🤖 Smart Chatbot", page_icon="🤖", layout="wide")

# ===== LOGIN SYSTEM (Optional) =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if (
            username == st.secrets["credentials"]["username"]
            and password == st.secrets["credentials"]["password"]
        ):
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

# ===== CHATBOT APP =====
st.title("🤖 Smart Chatbot with Image Generation")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== API Keys =====
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/v1/chat/completions"
IMAGE_API_URL = "https://api.groq.com/v1/images/generate"  # Change if using OpenAI or another provider

# ===== CHAT INPUT =====
user_input = st.text_input("💬 Your message:")
if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {"model": "llama3-8b-8192", "messages": st.session_state.messages}

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        bot_reply = data["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        st.error(f"Error contacting chatbot API: {e}")

# ===== DISPLAY CHAT HISTORY =====
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")

# ===== DOWNLOAD CHAT HISTORY =====
if st.button("📥 Download Chat History"):
    chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    b64 = base64.b64encode(chat_text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="chat_history.txt">Download Chat</a>'
    st.markdown(href, unsafe_allow_html=True)

# ===== FILE UPLOADS =====
uploaded_file = st.file_uploader("📂 Upload a file", type=["txt", "pdf", "docx"])
if uploaded_file:
    st.success(f"Uploaded file: {uploaded_file.name}")

# ===== IMAGE GENERATION =====
st.subheader("🎨 Image Generation")
image_prompt = st.text_input("Enter an image description:")
if st.button("Generate Image") and image_prompt:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {"prompt": image_prompt, "n": 1, "size": "512x512"}

    try:
        img_response = requests.post(IMAGE_API_URL, json=payload, headers=headers)
        img_response.raise_for_status()
        image_url = img_response.json()["data"][0]["url"]
        st.image(image_url, caption="Generated image", use_column_width=True)
    except Exception as e:
        st.error(f"Error generating image: {e}")
