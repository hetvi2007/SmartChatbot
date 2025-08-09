import streamlit as st
import requests
import base64

# Load API key from secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# App title
st.set_page_config(page_title="🤖 Smart Chatbot", page_icon="🤖")
st.title("🤖 Smart Chatbot with Image Generation")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("Type your message...")

if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Decide if prompt is for image generation
    if prompt.lower().startswith("generate image of"):
        image_desc = prompt.replace("generate image of", "").strip()

        # Example: Using a placeholder API (replace with your image API)
        img_url = f"https://image.pollinations.ai/prompt/{image_desc}"

        # Show image
        with st.chat_message("assistant"):
            st.image(img_url, caption=image_desc)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"![Generated Image]({img_url})"
        })

    else:
        # Call Groq API for text
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
        else:
            reply = f"Error: {response.text}"

        # Save assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Display assistant reply
        with st.chat_message("assistant"):
            st.markdown(reply)
