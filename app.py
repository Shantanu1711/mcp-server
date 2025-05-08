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
    if message["role"] == "user":
        st.markdown(f"""
        <div class="message-box">
            <strong>You:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message-box">
            <strong>Assistant:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)

# Chat input section (no form - fixes the double-click issue)
user_input = st.text_input(
    "Your question:",
    placeholder="Type your question here...",
    key="user_input"
)
send_button = st.button("Send")

# Handle user input
if send_button and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get response from MCP server
    with st.spinner("Thinking..."):
        response = send_message(user_input)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear input field
    st.session_state["user_input"] = ""

    # ✅ Rerun to force immediate UI update (works in old & new Streamlit)
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

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
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()
