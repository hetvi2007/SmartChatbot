import streamlit as st
import openai

# Load your API key securely from Streamlit Secrets
openai.api_key = st.secrets["openai"]["api_key"]

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
        # Use Chat Completions (OpenAI 1.x)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"⚠️ An error occurred: {str(e)}")
