import streamlit as st
import os
import json
from datetime import datetime
from groq import Groq
from PIL import Image
import io

# ----------- SETTINGS -----------
st.set_page_config(page_title="🤖 Smart Chatbot", layout="wide")

# ----------- AUTH (optional) -----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True  # Set to True if you don’t want login

# ----------- SECRETS -----------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

# ----------- SESSION STATE -----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------- SIDEBAR -----------
with st.sidebar:
    st.title("⚙️ Options")
    theme = st.radio("Theme", ["Light", "Dark"])
    if st.button("Download Chat History"):
        if st.session_state.messages:
            filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(st.session_state.messages, f)
            st.download_button("Download File", data=json.dumps(st.session_state.messages), file_name=filename)
    uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf", "png", "jpg"])

# ----------- MAIN CHAT UI -----------
st.title("🤖 Smart Chatbot")
user_input = st.text_input("Type your message:")
if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call LLM
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    )
    reply = completion.choices[0].message["content"]
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ----------- DISPLAY MESSAGES -----------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")

# ----------- IMAGE GENERATION FEATURE -----------
st.subheader("🎨 Image Generator")
img_prompt = st.text_input("Describe an image to generate:")
if st.button("Generate Image") and img_prompt:
    # Example: Use a fake image for now (replace with actual image generation API)
    img = Image.new("RGB", (512, 512), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # ✅ Fixed st.image line
    st.image(buf, caption="Generated Image", use_column_width=True)
