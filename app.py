import streamlit as st

# Title of the chatbot
st.title("💬 Smart Chatbot")
st.subheader("Ask me anything!")

# Session state to store conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.text_input("You:", "")

# Simple bot logic (replace with real AI if needed)
def get_bot_response(message):
    if "hello" in message.lower():
        return "Hi there! How can I help you?"
    elif "your name" in message.lower():
        return "I'm Smart Chatbot, your assistant!"
    elif "bye" in message.lower():
        return "Goodbye! Have a great day!"
    else:
        return "I'm still learning. Can you rephrase that?"

# When user submits input
if user_input:
    st.session_state.messages.append(("You", user_input))
    bot_response = get_bot_response(user_input)
    st.session_state.messages.append(("Bot", bot_response))

# Display conversation history
for sender, msg in st.session_state.messages:
    if sender == "You":
        st.write(f"**{sender}:** {msg}")
    else:
        st.write(f"🧠 **{sender}:** {msg}")
