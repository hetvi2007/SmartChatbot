import streamlit as st
import openai
import os

# Load API key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Page Config ---
st.set_page_config(page_title="Smart Chatbot", page_icon="💬", layout="centered")

# --- App Title ---
st.title("🤖 Smart Chatbot")
st.caption("Talk to an intelligent bot that understands and responds contextually.")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# --- Chat Input ---
user_input = st.text_input("You:", placeholder="Type your message here...")

# --- Chat Response Logic ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error("Failed to get response from OpenAI. Check your API key and try again.")
        st.stop()

# --- Display Chat History ---
for message in st.session_state.messages[1:]:
    is_user = message["role"] == "user"
    with st.chat_message("user" if is_user else "assistant"):
        st.write(message["content"])
