import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Insurance & AngelOne Chatbot",
    page_icon="🤖",
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
    }
    .source-info {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("🤖 Insurance & AngelOne Chatbot")
st.markdown("Ask questions about insurance policies and AngelOne services!")

# Chat input
user_input = st.text_input("Your question:", key="user_input", placeholder="Type your question here...")

def send_message(message):
    """Send message to MCP server and get response."""
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"text": message}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Display chat history
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong>
                <div class="message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Format sources if available
            sources_html = ""
            if "sources" in message:
                sources = message["sources"]
                sources_html = f"""
                <div class="source-info">
                    Sources:
                    <ul>
                        {''.join(f'<li>{source["source"]} (Page {source.get("page", "N/A")})</li>' for source in sources)}
                    </ul>
                </div>
                """
            
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong>
                <div class="message-content">{message["content"]}</div>
                {sources_html}
            </div>
            """, unsafe_allow_html=True)

# Handle user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response from MCP server
    response = send_message(user_input)
    
    if "error" in response:
        st.error(f"Error: {response['error']}")
    else:
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["response"],
            "sources": response.get("sources", [])
        })
    
    # Clear input
    st.session_state.user_input = ""
    
    # Rerun to update chat history
    st.experimental_rerun()

# Sidebar with instructions
with st.sidebar:
    st.markdown("""
    ## How to use
    1. The chatbot has access to:
       - Insurance policy PDFs
       - AngelOne website content
    2. Ask questions about:
       - Policy details
       - Coverage information
       - AngelOne services
       - Trading features
    
    ## Features
    - Semantic search across documents
    - Context-aware responses
    - Source citations
    - Powered by Claude 3
    """)
    
    # Display document statistics
    st.markdown("### Document Statistics")
    pdf_count = len([f for f in os.listdir("data/pdfs") if f.endswith('.pdf')])
    webpage_count = len([f for f in os.listdir("data/webpages") if f.endswith('.txt')])
    
    st.markdown(f"""
    - PDF Documents: {pdf_count}
    - Web Pages: {webpage_count}
    """) 