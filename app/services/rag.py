import json
import os
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

_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "documents")
os.makedirs(_STORAGE_DIR, exist_ok=True)


def _thread_paths(thread_id: str) -> tuple[str, str]:
    pdf_path = os.path.join(_STORAGE_DIR, f"{thread_id}.pdf")
    meta_path = os.path.join(_STORAGE_DIR, f"{thread_id}.json")
    return pdf_path, meta_path


def _write_metadata(thread_id: str, metadata: dict) -> None:
    _, meta_path = _thread_paths(thread_id)
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle)


def _read_metadata(thread_id: str) -> Optional[dict]:
    _, meta_path = _thread_paths(thread_id)
    if not os.path.exists(meta_path):
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        print(f"[DEBUG RAG] Failed to read metadata for thread {thread_id}: {exc}")
        return None


def _build_retriever_from_pdf(pdf_path: str, embeddings: Any) -> Any:
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    return retriever, len(docs), len(chunks)


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available or rehydrate from disk."""
    if not thread_id:
        return None

    thread_key = str(thread_id)
    if thread_key in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_key]

    metadata = _THREAD_METADATA.get(thread_key) or _read_metadata(thread_key)
    if metadata:
        _THREAD_METADATA[thread_key] = metadata
        pdf_path = metadata.get("file_path")
        if pdf_path and os.path.exists(pdf_path):
            if _DEFAULT_EMBEDDINGS is None:
                print("[DEBUG RAG] Embeddings not available to rebuild retriever")
                return None
            try:
                retriever, docs_count, chunks_count = _build_retriever_from_pdf(pdf_path, _DEFAULT_EMBEDDINGS)
                _THREAD_RETRIEVERS[thread_key] = retriever
                metadata.update({
                    "documents": docs_count,
                    "chunks": chunks_count
                })
                _THREAD_METADATA[thread_key] = metadata
                _write_metadata(thread_key, metadata)
                return retriever
            except Exception as exc:
                print(f"[DEBUG RAG] Failed to rebuild retriever for thread {thread_key}: {exc}")
                return None

    print(f"[DEBUG RAG] Retriever not found for thread {thread_id}")
    print(f"[DEBUG RAG] Available threads: {list(_THREAD_RETRIEVERS.keys())}")
    print(f"[DEBUG RAG] Metadata threads: {list(_THREAD_METADATA.keys())}")
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

    pdf_path, _ = _thread_paths(str(thread_id))
    with open(pdf_path, "wb") as handle:
        handle.write(file_bytes)

    retriever, docs_count, chunks_count = _build_retriever_from_pdf(pdf_path, embeddings)

    metadata = {
        "filename": filename or os.path.basename(pdf_path),
        "documents": docs_count,
        "chunks": chunks_count,
        "file_path": pdf_path,
    }

    _THREAD_RETRIEVERS[str(thread_id)] = retriever
    _THREAD_METADATA[str(thread_id)] = metadata
    _write_metadata(str(thread_id), metadata)

    return {
        "filename": metadata["filename"],
        "documents": metadata["documents"],
        "chunks": metadata["chunks"],
    }


def retrieve_from_document(query: str, thread_id: str) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    Returns context and metadata from the document.
    """
    print(f"[DEBUG RAG] Attempting to retrieve for thread: {thread_id}")
    retriever = _get_retriever(thread_id)
    if retriever is None:
        # Check if we have metadata but lost the retriever (server restart)
        if str(thread_id) in _THREAD_METADATA or _read_metadata(str(thread_id)):
            return {
                "error": "Document metadata exists but retriever was lost. Please re-upload the document.",
                "query": query,
            }
        return {
            "error": "No document indexed for this chat. Upload a PDF first.",
            "query": query,
        }

    # Use the retriever API to fetch relevant documents
    try:
        print(f"[DEBUG RAG] Calling retriever.get_relevant_documents with query: {query[:50]}...")
        results = retriever.get_relevant_documents(query)
        print(f"[DEBUG RAG] Successfully retrieved {len(results)} documents")
    except AttributeError as ae:
        print(f"[DEBUG RAG] AttributeError: {ae}, trying invoke method")
        try:
            results = retriever.invoke(query)
            print(f"[DEBUG RAG] Successfully retrieved {len(results)} documents via invoke")
        except Exception as e:
            print(f"[DEBUG RAG] Invoke also failed: {e}")
            return {"error": f"Retriever invocation failed: {e}", "query": query}
    except Exception as e:
        print(f"[DEBUG RAG] Exception during retrieval: {type(e).__name__}: {e}")
        return {"error": f"Retrieval failed: {e}", "query": query}

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
    thread_key = str(thread_id)
    has_retriever = thread_key in _THREAD_RETRIEVERS
    metadata = _THREAD_METADATA.get(thread_key) or _read_metadata(thread_key)
    has_file = bool(metadata and metadata.get("file_path") and os.path.exists(metadata["file_path"]))
    print(f"[DEBUG RAG] has_document check - thread: {thread_id}, retriever: {has_retriever}, metadata: {bool(metadata)}, file: {has_file}")
    # Return True if retriever exists or stored file exists to allow rehydration
    return has_retriever or has_file


def get_document_info(thread_id: str) -> Optional[dict]:
    """Get metadata about the uploaded document for a thread."""
    thread_key = str(thread_id)
    metadata = _THREAD_METADATA.get(thread_key) or _read_metadata(thread_key)
    if metadata and metadata.get("file_path") and os.path.exists(metadata["file_path"]):
        _THREAD_METADATA[thread_key] = metadata
        return metadata
    return None
