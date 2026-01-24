"""
RAG (Retrieval Augmented Generation) Service
Handles PDF upload, processing, and document retrieval
"""

import os
import tempfile
from typing import Dict, Any, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize HuggingFace embeddings
try:
    _DEFAULT_EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    print(f"⚠ HuggingFaceEmbeddings initialization failed: {e}")
    _DEFAULT_EMBEDDINGS = None


_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""
    if thread_id and str(thread_id) in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[str(thread_id)]
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None, embeddings: Optional[Any] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.

    Returns a summary dict that can be surfaced in the UI.
    """
    if embeddings is None:
        embeddings = _DEFAULT_EMBEDDINGS

    if embeddings is None:
        raise ValueError(
            "No embeddings available. Provide an `embeddings` instance to `ingest_pdf` or install/configure HuggingFaceEmbeddings."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200, 
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

        _THREAD_RETRIEVERS[str(thread_id)] = retriever
        _THREAD_METADATA[str(thread_id)] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        # The FAISS store keeps copies of the text, so the temp file is safe to remove.
        try:
            os.remove(temp_path)
        except OSError:
            pass


def retrieve_from_document(query: str, thread_id: str) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Returns context and metadata from the document.
    """
    retriever = _get_retriever(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    # Use the retriever API to fetch relevant documents
    try:
        results = retriever.get_relevant_documents(query)
    except AttributeError:
        try:
            results = retriever.retrieve(query)
        except Exception as e:
            return {"error": f"Retriever invocation failed: {e}", "query": query}

    context = [doc.page_content for doc in results]
    metadata = [getattr(doc, "metadata", {}) for doc in results]

    return {
        "query": query,
        "context": context,
        "metadata": metadata,
        "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
    }


def has_document(thread_id: str) -> bool:
    """Check if a thread has an uploaded document."""
    return str(thread_id) in _THREAD_RETRIEVERS


def get_document_info(thread_id: str) -> Optional[dict]:
    """Get metadata about the uploaded document for a thread."""
    return _THREAD_METADATA.get(str(thread_id))
