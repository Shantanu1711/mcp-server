import streamlit as st
import requests
import json
import logging
import html
import os

# Configure logging (can control via env var)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure the page
st.set_page_config(
    page_title="Document Chatbot",
    page_icon="📄",
    layout="wide"
)

# Custom CSS: white background, black text, simple boxes
st.markdown("""
<style>
    body, .stApp {
        background-color: white !important;
        color: black !important;
    }
    .message-box {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
        color: black;
        font-size: 1.1rem;
    }
    .stTextInput>div>div>input {
        font-size: 1.2rem;
        background-color: white;
        color: black;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📄 Document Chatbot")
st.markdown("Ask questions about your documents!")

# Get API URL from secrets or fallback to localhost
API_URL = st.secrets.get("BACKEND_API_URL", "http://localhost:8000/chat")

# Function to send message to MCP server
def send_message(message):
    try:
        logging.debug(f"Sending message: {message}")
        response = requests.post(
            API_URL,
            json={"text": message}
        )
        logging.debug(f"Response status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            if "response" in response_data:
                return response_data["response"]
            else:
                return f"Unexpected response format: {response_data}"
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except json.JSONDecodeError:
                error_detail = response.text  # fallback to raw text
            return f"Error: Server returned status code {response.status_code}\nDetails: {error_detail}"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to the server at {API_URL}. Please check if it's running."
    except Exception as e:
        logging.exception("Unexpected error occurred")
        return f"Error: {str(e)}"

# Input and button
user_input = st.text_input("Your question:", placeholder="Type your question here...")
send_button = st.button("Send")

# Handle send click
if send_button and user_input:
    # Display user question immediately
    st.markdown(f"""
    <div class="message-box">
        <strong>You:</strong><br>{html.escape(user_input)}
    </div>
    """, unsafe_allow_html=True)

    # Get response and display immediately
    with st.spinner("Thinking..."):
        response = send_message(user_input)

    st.markdown(f"""
    <div class="message-box">
        <strong>Assistant:</strong><br>{html.escape(response)}
    </div>
    """, unsafe_allow_html=True)
