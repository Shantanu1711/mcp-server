import chromadb
from chromadb.config import Settings
import streamlit as st
import pandas as pd
from pathlib import Path

def view_chromadb():
    """View contents of ChromaDB collection."""
    st.title("ChromaDB Contents Viewer")
    
    # Initialize ChromaDB client
    client = chromadb.Client(Settings(
        persist_directory="pinecone_db",
        anonymized_telemetry=False
    ))
    
    try:
        # Get the collection
        collection = client.get_collection("documents")
        
        # Get all items from the collection
        results = collection.get()
        
        if not results['ids']:
            st.warning("No documents found in the collection.")
            return
        
        # Create a DataFrame for better display
        data = {
            'Document ID': results['ids'],
            'Source': [metadata.get('source', 'N/A') for metadata in results['metadatas']],
            'Chunk Index': [metadata.get('chunk_index', 'N/A') for metadata in results['metadatas']],
            'Content': results['documents']
        }
        
        df = pd.DataFrame(data)
        
        # Display statistics
        st.subheader("Collection Statistics")
        st.write(f"Total Documents: {len(results['ids'])}")
        st.write(f"Unique Sources: {len(set(data['Source']))}")
        
        # Display the data
        st.subheader("Document Contents")
        
        # Add search functionality
        search_term = st.text_input("Search in documents:", "")
        
        if search_term:
            filtered_df = df[df['Content'].str.contains(search_term, case=False)]
            st.write(f"Found {len(filtered_df)} matching documents")
            df = filtered_df
        
        # Display documents in an expandable format
        for idx, row in df.iterrows():
            with st.expander(f"Document {row['Document ID']} - Source: {Path(row['Source']).name}"):
                st.write("**Source:**", row['Source'])
                st.write("**Chunk Index:**", row['Chunk Index'])
                st.write("**Content:**")
                st.text(row['Content'])
        
        # Add download option
        if st.button("Download as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="chromadb_contents.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Error accessing ChromaDB: {str(e)}")
        st.info("Make sure you have processed documents using process_documents.py first.")

if __name__ == "__main__":
    view_chromadb()