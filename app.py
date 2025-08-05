import streamlit as st
import requests
import base64

# Load API key securely
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image"

# Setup Streamlit
st.set_page_config(page_title="Smart Chatbot", page_icon="🤖")
st.title("🤖 Smart Chatbot + 🎨 Image Generator")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# Display chat history
for msg in st.session_state.messages[1:]:  # skip system message
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Detect image prompt
def is_image_prompt(text):
    keywords = ["draw", "generate image", "create an image", "make a picture", "show me", "visualize"]
    return any(keyword in text.lower() for keyword in keywords)

# Generate image from Stability AI
def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 8,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }
    response = requests.post(STABILITY_API_URL, headers=headers, json=json_data)

    if response.status_code == 200:
        image_data = response.json()["artifacts"][0]["base64"]
        return image_data
    else:
        st.error("Failed to generate image.")
        return None

# Chat input
user_input = st.chat_input("Say something...")

if user_input:
    # Show user input
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Image prompt
    if is_image_prompt(user_input):
        with st.chat_message("assistant"):
            st.markdown("🖼 Generating an image for your prompt...")
            img_data = generate_image(user_input)
            if img_data:
                st.image(base64.b64decode(img_data), caption="Generated Image")
        st.session_state.messages.append({"role": "assistant", "content": "Generated an image above."})

    # Text response (Groq API)
    else:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": st.session_state.messages,
            "temperature": 0.7
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.error("❌ Failed to get response from Groq API.")
