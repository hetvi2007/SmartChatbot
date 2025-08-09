import streamlit as st
import requests
import os
from datetime import datetime
from werkzeug.security import check_password_hash

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🤖 Smart Chatbot", layout="wide")

# ---------------- SECRETS ----------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  # Make sure this is in secrets.toml

# Optional login credentials
USERNAME = st.secrets.get("credentials", {}).get("username")
PASSWORD_HASH = st.secrets.get("credentials", {}).get("password_hash")

# ---------------- LOGIN ----------------
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    skip = st.sidebar.checkbox("Skip login")

    if skip:
        st.session_state.logged_in = True
        return True

    if st.sidebar.button("Login"):
        if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
            st.session_state.logged_in = True
            st.success("✅ Login successful")
            return True
        else:
            st.error("❌ Invalid username or password")
    return False

# ---------------- CHATBOT FUNCTION ----------------
def groq_chat(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# ---------------- IMAGE GENERATION ----------------
def generate_image(prompt):
    url = "https://api.groq.com/openai/v1/images/generations"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "512x512"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["data"][0]["url"]
    else:
        st.error(f"Image Error: {response.status_code} - {response.text}")
        return None

# ---------------- MAIN APP ----------------
if login():
    st.title("🤖 Smart Chatbot")

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar
    st.sidebar.header("⚙️ Options")
    if st.sidebar.button("🆕 New Chat"):
        st.session_state.chat_history = []
    search_term = st.sidebar.text_input("🔍 Search in chats")

    uploaded_file = st.sidebar.file_uploader("📂 Upload a file", type=["txt", "pdf", "docx"])
    if uploaded_file:
        st.sidebar.success(f"Uploaded: {uploaded_file.name}")

    # Chat input
    user_input = st.text_input("💬 Ask me something...")
    if st.button("Send") and user_input:
        answer = groq_chat(user_input)
        if answer:
            st.session_state.chat_history.append({"question": user_input, "answer": answer})

    # Image generation
    img_prompt = st.text_input("🎨 Image prompt")
    if st.button("Generate Image") and img_prompt:
        img_url = generate_image(img_prompt)
        if img_url:
            st.session_state.generated_image = img_url

    # Show chat history
    st.subheader("📜 Chat History")
    for chat in st.session_state.chat_history:
        if not search_term or search_term.lower() in chat["question"].lower() or search_term.lower() in chat["answer"].lower():
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**Bot:** {chat['answer']}")

    # Show generated image
    if "generated_image" in st.session_state:
        st.image(st.session_state.generated_image, caption="Generated Image", use_column_width=True)

    # Download chat
    if st.session_state.chat_history:
        chat_text = "\n\n".join([f"You: {c['question']}\nBot: {c['answer']}" for c in st.session_state.chat_history])
        st.download_button("💾 Download Chat", data=chat_text, file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

