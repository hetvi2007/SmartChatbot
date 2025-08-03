import streamlit as st
import requests

# Load Groq API key from Streamlit Secrets
GROQ_API_KEY = st.secrets["groq"]["api_key"]

st.set_page_config(page_title="Smart Chatbot", page_icon="🤖")
st.title("💬 Your Smart Python Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful and smart assistant."}
    ]

# Display chat history
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
user_input = st.chat_input("Say something...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",  # or "mixtral-8x7b-32768"
        "messages": st.session_state.messages
    }

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()
        reply = res.json()["choices"][0]["message"]["content"]
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")
