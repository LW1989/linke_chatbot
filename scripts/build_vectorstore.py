#!/usr/bin/env python3
"""
build_vectorstore.py
--------------------------------
Build or update the vector store from PDF and TXT files.

Usage:
    python build_vectorstore.py

Dependencies:
    pip install langchain chromadb
"""

import os
import logging
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma

# === CONFIGURATION ============================================================
PDF_DIR = "../internal_docs"  # Directory containing PDF files
TXT_DIR = "../extracted_text"  # Directory containing TXT files
VECTORSTORE_DIR = "../chroma_db"  # Directory to save the vector store
# ==============================================================================

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_documents() -> list:
    """
    Load documents from PDF and TXT files.
    """
    documents = []

    # Load PDFs
    for filename in os.listdir(PDF_DIR):
        if filename.endswith('.pdf'):
            file_path = os.path.join(PDF_DIR, filename)
            logger.info(f"Loading PDF: {filename}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

    # Load TXTs
    for filename in os.listdir(TXT_DIR):
        if filename.endswith('.txt'):
            file_path = os.path.join(TXT_DIR, filename)
            logger.info(f"Loading TXT: {filename}")
            loader = TextLoader(file_path)
            documents.extend(loader.load())

    return documents


def build_vectorstore() -> None:
    """
    Build or update the vector store from documents.
    """
    documents = load_documents()
    if not documents:
        logger.warning("No documents found to build vector store.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Process in batches of 5000 (below Chroma's limit of 5461)
    batch_size = 5000
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1} of {(len(texts) + batch_size - 1)//batch_size}")
        
        if i == 0:
            # First batch: create new vectorstore
            vectorstore = Chroma.from_documents(batch, embeddings, persist_directory=VECTORSTORE_DIR)
        else:
            # Subsequent batches: add to existing vectorstore
            vectorstore.add_documents(batch)
    
    vectorstore.persist()
    logger.info(f"Vector store built and saved in: {os.path.abspath(VECTORSTORE_DIR)}")


if __name__ == "__main__":
    build_vectorstore() 