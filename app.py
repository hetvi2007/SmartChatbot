import streamlit as st
import requests

# Load your API key securely from Streamlit Secrets
GROQ_API_KEY = st.secrets["groq"]["api_key"]

st.set_page_config(page_title="Smart Chatbot", page_icon="🤖")
st.title("💬 Your Smart Python Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful and smart assistant."}
    ]

# Display past messages
for msg in st.session_state.messages[1:]:  # skip system message
    st.chat_message(msg["role"]).write(msg["content"])

# Input box
user_input = st.chat_input("Say something...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Groq-compatible OpenAI API call
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mixtral-8x7b-32768",  # or "llama2-70b-4096", etc.
                "messages": st.session_state.messages,
                "temperature": 0.7
            }
        )
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")
