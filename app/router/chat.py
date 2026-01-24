from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from app.schema.models import (
    ChatRequest,
    ChatResponse,
    ThreadListResponse,
    ThreadHistoryResponse,
    UpdateTitleRequest,
    NewThreadResponse,
    PDFUploadResponse,
    MessageResponse,
    ThreadResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    DocumentInfoResponse
)
from app.services.chat_service import ChatService
from app.services.rag_service import ingest_pdf, retrieve_from_document, has_document, get_document_info
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

chat_router = APIRouter()


@chat_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot and get a response.
    If thread_id is not provided, a new thread will be created.
    """
    try:
        # Create new thread if not provided
        if not request.thread_id:
            thread_id = ChatService.create_new_thread()
        else:
            thread_id = request.thread_id
        
        # Generate thread title from first message if needed
        ChatService.get_or_create_thread_title(thread_id, request.message)
        
        # Send message and get response
        result = ChatService.send_message(request.message, thread_id)
        
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses in real-time.
    Returns a streaming response with message chunks.
    """
    try:
        # Create new thread if not provided
        if not request.thread_id:
            thread_id = ChatService.create_new_thread()
        else:
            thread_id = request.thread_id
        
        # Generate thread title from first message if needed
        ChatService.get_or_create_thread_title(thread_id, request.message)
        
        def generate_stream():
            """Generator function for streaming responses"""
            try:
                for chunk in ChatService.stream_message(request.message, thread_id):
                    # Send each chunk as JSON
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send final message with thread_id
                yield f"data: {json.dumps({'thread_id': thread_id, 'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/threads", response_model=ThreadListResponse)
async def get_threads():
    """
    Get all chat threads with their titles.
    Returns threads in reverse chronological order.
    """
    try:
        threads = ChatService.get_all_threads()
        
        # Convert to response model
        thread_responses = [
            ThreadResponse(thread_id=t["thread_id"], title=t["title"])
            for t in threads
        ]
        
        # Reverse order to show newest first
        return ThreadListResponse(threads=list(reversed(thread_responses)))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.get("/threads/{thread_id}", response_model=ThreadHistoryResponse)
async def get_thread_history(thread_id: str):
    """
    Get the conversation history for a specific thread.
    Returns all messages in the thread.
    """
    try:
        messages = ChatService.load_conversation(thread_id)
        
        # For new threads with no messages, return empty list instead of 404
        # The thread exists if it's in the thread metadata
        if not messages:
            from app.services.chatbot_service import get_thread_title_from_db
            thread_exists = get_thread_title_from_db(thread_id) is not None
            
            if not thread_exists:
                raise HTTPException(status_code=404, detail="Thread not found")
        
        # Convert to response model
        message_responses = [
            MessageResponse(content=m["content"], type=m["type"])
            for m in messages
        ]
        
        return ThreadHistoryResponse(
            thread_id=thread_id,
            messages=message_responses
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/threads/new", response_model=NewThreadResponse)
async def create_new_thread():
    """
    Create a new chat thread.
    Returns the new thread ID.
    """
    try:
        thread_id = ChatService.create_new_thread()
        return NewThreadResponse(thread_id=thread_id, title="New Chat")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.put("/threads/{thread_id}/title")
async def update_thread_title(thread_id: str, request: UpdateTitleRequest):
    """
    Update the title of a thread.
    """
    try:
        success = ChatService.update_thread_title(thread_id, request.title)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update title")
        
        return {"status": "success", "thread_id": thread_id, "title": request.title}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    thread_id: Optional[str] = None
):
    """
    Upload a PDF file for RAG (Retrieval Augmented Generation).
    The PDF will be processed and indexed for the specified thread.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create new thread if not provided
        if not thread_id:
            thread_id = ChatService.create_new_thread()
        
        # Read file bytes
        file_bytes = await file.read()
        
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Process PDF using the existing rag_backend logic
        result = ingest_pdf(
            file_bytes=file_bytes,
            thread_id=thread_id,
            filename=file.filename
        )
        
        # Add thread_id to result
        result["thread_id"] = thread_id
        
        return PDFUploadResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@chat_router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Delete a thread (placeholder - implement if needed).
    Note: LangGraph checkpointer doesn't have built-in delete,
    so this would require custom implementation.
    """
    # This is a placeholder - implement if you need thread deletion
    return {
        "status": "not_implemented",
        "message": "Thread deletion not yet implemented"
    }


@chat_router.post("/query-document", response_model=DocumentQueryResponse)
async def query_document(request: DocumentQueryRequest):
    """
    Query an uploaded document and get AI-generated answers.
    This endpoint retrieves relevant context from the document and generates an answer.
    """
    try:
        # Check if document exists
        if not has_document(request.thread_id):
            raise HTTPException(
                status_code=404,
                detail="No document found for this thread. Please upload a PDF first."
            )
        
        # Retrieve relevant context from document
        retrieval_result = retrieve_from_document(request.query, request.thread_id)
        
        if "error" in retrieval_result:
            raise HTTPException(status_code=500, detail=retrieval_result["error"])
        
        # Generate answer using the context
        context_text = "\n\n".join(retrieval_result["context"])
        
        # Use LLM to generate answer based on context
        llm = ChatGroq(model="qwen/qwen3-32b")
        prompt = f"""Based on the following context from a document, answer the question.

Context:
{context_text}

Question: {request.query}

Provide a clear and concise answer based only on the information in the context. If the context doesn't contain relevant information, say so.

Answer:"""
        
        response = llm.invoke(prompt)
        answer = response.content
        
        return DocumentQueryResponse(
            answer=answer,
            context=retrieval_result["context"],
            source_file=retrieval_result.get("source_file"),
            thread_id=request.thread_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query document: {str(e)}")


@chat_router.get("/threads/{thread_id}/document", response_model=DocumentInfoResponse)
async def get_thread_document_info(thread_id: str):
    """
    Get information about the document uploaded for a specific thread.
    Returns whether a document exists and its metadata.
    """
    try:
        has_doc = has_document(thread_id)
        
        if has_doc:
            doc_info = get_document_info(thread_id)
            return DocumentInfoResponse(
                has_document=True,
                filename=doc_info.get("filename"),
                documents=doc_info.get("documents"),
                chunks=doc_info.get("chunks"),
                thread_id=thread_id
            )
        else:
            return DocumentInfoResponse(
                has_document=False,
                thread_id=thread_id
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
