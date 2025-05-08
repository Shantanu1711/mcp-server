# Customer Support RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot trained on customer support documentation to assist users by answering queries and providing relevant support information.

## Features

- Answers questions based on provided customer support documentation
- Responds with "I don't know" for questions outside the documentation scope
- User-friendly web interface
- Semantic search for relevant information
- Context-aware responses
- Web scraping support for AngelOne documentation
- PDF processing for insurance documents

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
HF_API_KEY=your_huggingface_api_key_here
```

5. Gather documentation:
   - For AngelOne documentation:
     ```bash
     python scrape_angelone.py
     ```
   - For insurance PDFs:
     - Place all insurance PDFs in the `docs/insurance` directory

6. Process the documentation:
```bash
python process_documents.py
```

7. Start the backend server:
```bash
python mcp_server.py
```

8. In a new terminal, start the frontend:
```bash
streamlit run app.py
```

## Deployment

To deploy the application:

1. Backend (FastAPI):
   - Deploy to a cloud platform (e.g., Heroku, AWS, DigitalOcean)
   - Set environment variables in the cloud platform
   - Use a process manager (e.g., Gunicorn) to run the FastAPI server

2. Frontend (Streamlit):
   - Deploy to Streamlit Cloud or similar platform
   - Configure the frontend to point to your deployed backend URL
   - Set environment variables in the deployment platform

## Usage

1. Open your web browser and navigate to the deployed URL
2. Type your question in the chat interface
3. The chatbot will:
   - Search the documentation for relevant information
   - Generate a response based on the found information
   - Respond with "I don't know" if the information is not in the documentation

## Project Structure

```
.
├── app.py                 # Streamlit frontend
├── mcp_server.py         # FastAPI backend
├── process_documents.py  # Document processing script
├── scrape_angelone.py    # Web scraper for AngelOne docs
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── docs/               # Documentation directory
│   ├── angelone/      # Scraped AngelOne documentation
│   └── insurance/     # Insurance PDFs
└── chroma_db/         # Vector database storage
```

## Dependencies

- FastAPI: Backend API
- Streamlit: Frontend interface
- Hugging Face: LLM for response generation
- ChromaDB: Vector database for document storage
- Sentence Transformers: Text embeddings
- PyPDF: PDF processing
- BeautifulSoup4: Web scraping
- Requests: HTTP client

## Notes

- The chatbot only answers questions based on the provided documentation
- It will respond with "I don't know" for questions outside the documentation scope
- The system uses semantic search to find relevant information
- Responses are generated using the Hugging Face API
- Web scraping is rate-limited to be respectful to the source website

## License

[Your License Here] 