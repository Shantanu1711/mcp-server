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
    page_title="PDF Chatbot",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTextInput>div>div>input {
        font-size: 1.2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #2b313e;
    }
    .assistant-message {
        background-color: #1e1e1e;
    }
    .message-content {
        margin-top: 0.5rem;
        white-space: pre-wrap;
        font-size: 1.1rem;
        line-height: 1.5;
    }
    .error-message {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("📚 PDF Chatbot")
st.markdown("Ask questions about your PDF documents!")

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

# Display chat history
for message in st.session_state.messages:
    content = html.escape(message["content"])  # escape for safety
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong>
                <div class="message-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if the message is an error
            if message["content"].startswith("Error:"):
                st.markdown(f"""
                <div class="chat-message error-message">
                    <strong>Error:</strong>
                    <div class="message-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Assistant:</strong>
                    <div class="message-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)

# Chat input
with st.form(key="chat_form"):
    user_input = st.text_input("Your question:", placeholder="Type your question here...")
    submit_button = st.form_submit_button("Send")

# Handle user input
if submit_button and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response from MCP server
    with st.spinner("Thinking..."):
        response = send_message(user_input)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with instructions & Clear Chat button
with st.sidebar:
    st.markdown("""
    ## How to use
    1. Place your PDF files in the `docs` directory
    2. Run `process_documents.py` to process the PDFs
    3. Start the MCP server with `python mcp_server.py`
    4. Ask questions about your documents!
    
    ## Features
    - PDF document processing
    - Semantic search
    - Context-aware responses
    - Powered by Hugging Face
    """)
    
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()
