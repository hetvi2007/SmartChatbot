import streamlit as st
from openai import OpenAI
from werkzeug.security import check_password_hash, generate_password_hash

# Load API key securely
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Setup client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ---------- Login Config ----------
USERS = {
    "admin": generate_password_hash("admin123"),
    "guest": generate_password_hash("guest123"),
}

def login():
    with st.sidebar:
        st.subheader("🔐 Login or Skip")
        choice = st.radio("Choose an option:", ["Login", "Continue without login"])
        
        if choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username in USERS and check_password_hash(USERS[username], password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials.")
        else:
            if st.button("Skip Login"):
                st.session_state.logged_in = True
                st.session_state.username = "Guest"
                st.experimental_rerun()

# ---------- Main App ----------

def main_chat():
    st.set_page_config(page_title="Smart Chatbot", page_icon="🤖")
    st.title("💬 Smart Chatbot")

    # Start chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful and smart assistant."}
        ]

    # Sidebar controls
    with st.sidebar:
        st.write(f"👤 Logged in as: `{st.session_state.username}`")
        if st.button("🆕 Start New Chat"):
            st.session_state.messages = [
                {"role": "system", "content": "You are a helpful and smart assistant."}
            ]
            st.experimental_rerun()

    # Display chat history
    for msg in st.session_state.messages[1:]:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input
    user_input = st.chat_input("Ask me anything...")
    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.chat_message("assistant").write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# ---------- Launcher ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_chat()
