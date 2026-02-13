from typing import Optional, List, Dict, Any
from datetime import datetime, date
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.services.chatbot import (
    chatbot,
    retrieve_all_threads,
    save_thread_title,
    get_thread_title_from_db,
    get_all_thread_metadata,
    touch_thread
)
from app.services.thread import generate_thread_id, generate_id_name
from app.services.rag import has_document

class ChatService:
    """Service class to handle chat-related business logic"""
    
    @staticmethod
    def create_new_thread() -> str:
        """Create a new thread and return its ID"""
        thread_id = generate_thread_id()
        save_thread_title(thread_id, "New Chat")
        return thread_id
    
    @staticmethod
    def get_or_create_thread_title(thread_id: str, user_message: Optional[str] = None) -> str:
        db_title = get_thread_title_from_db(thread_id)
        
        # If title is "New Chat" (default), generate a new one from the message
        if db_title and db_title != "New Chat":
            return db_title
        
        # Generate new title from user message
        if user_message:
            try:
                title = generate_id_name(user_message)
                save_thread_title(thread_id, title)
                return title
            except Exception as e:
                print(f"Error generating title: {e}")
                return str(thread_id)[:8] + "..."
        
        return str(thread_id)[:8] + "..."
    
    @staticmethod
    def get_all_threads() -> List[Dict[str, str]]:
        thread_ids = retrieve_all_threads()
        metadata = get_all_thread_metadata()
        
        threads = []
        for tid in thread_ids:
            thread_meta = metadata.get(tid, {})
            title = thread_meta.get("title", "New Chat") if isinstance(thread_meta, dict) else thread_meta
            updated_at = thread_meta.get("updated_at") if isinstance(thread_meta, dict) else None
            threads.append({
                "thread_id": tid,
                "title": title,
                "updated_at": updated_at
            })
        
        # Sort by updated_at descending (most recent first)
        threads.sort(key=lambda x: x.get("updated_at") or datetime.min, reverse=True)
        
        return threads
    
    @staticmethod
    def load_conversation(thread_id: str) -> List[Dict[str, str]]:
        try:
            state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
            messages = state.values.get("messages", [])
            
            formatted_messages = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    formatted_messages.append({
                        "content": message.content,
                        "type": "human"
                    })
                elif isinstance(message, AIMessage):
                    if message.content:
                        formatted_messages.append({
                            "content": message.content,
                            "type": "ai"
                        })
            
            return formatted_messages
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []
    
    @staticmethod
    def send_message(message: str, thread_id: str, tools: Optional[List[str]] = None) -> Dict[str, Any]:
        config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {"thread_id": thread_id}
        }
        
        try:
            # If blogs tool is requested, use the blog app
            if tools and "blogs" in tools:
                try:
                    from app.tools.blogs.graph import app as blog_app
                    
                    blog_state = {
                        "topic": message,
                        "as_of": date.today().isoformat(),
                    }
                    
                    final_state = blog_app.invoke(blog_state)
                    
                    # Update thread timestamp
                    touch_thread(thread_id)
                    
                    return {
                        "response": final_state.get("final", "Blog generated successfully"),
                        "thread_id": thread_id,
                        "tool_used": "blogs"
                    }
                except Exception as blog_error:
                    error_msg = str(blog_error)
                    print(f"Error using blog tool: {error_msg}")
                    
                    # Provide user-friendly error messages
                    if "name resolution failed" in error_msg or "503" in error_msg:
                        return {
                            "response": "⚠️ **Blog Generation Failed**\n\nThe blog generation service is currently unavailable (network connection issue). This could be due to:\n- External API service is down\n- Network connectivity issues\n- DNS resolution problems\n\nPlease try again later or use the regular chat without the blog tool.",
                            "thread_id": thread_id,
                            "tool_used": "blogs"
                        }
                    else:
                        return {
                            "response": f"⚠️ **Blog Generation Failed**\n\nAn error occurred while generating the blog:\n```\n{error_msg}\n```\n\nPlease try again or use the regular chat without the blog tool.",
                            "thread_id": thread_id,
                            "tool_used": "blogs"
                        }
            
            # Check if thread has a document
            doc_exists = has_document(thread_id)
            
            # Invoke chatbot with user message
            final_state = chatbot.invoke(
                {
                    "messages": [HumanMessage(content=message)],
                    "has_document": doc_exists,
                    "thread_id": thread_id
                },
                config=config
            )
            
            messages = final_state["messages"]
            
            # Update thread timestamp to show recent activity
            touch_thread(thread_id)
            
            # Extract the last AI message
            ai_response = None
            has_tool_calls = False
            
            for msg in reversed(messages):
                if isinstance(msg, ToolMessage):
                    has_tool_calls = True
                if isinstance(msg, AIMessage) and not ai_response:
                    ai_response = msg.content
                    break
            
            return {
                "response": ai_response or "No response generated",
                "thread_id": thread_id,
                "has_tool_calls": has_tool_calls
            }
        except Exception as e:
            print(f"Error sending message: {e}")
            raise Exception(f"Failed to send message: {str(e)}")
    
    @staticmethod
    def stream_message(message: str, thread_id: str, tools: Optional[List[str]] = None):
        config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {"thread_id": thread_id}
        }
        
        try:
            # If blogs tool is requested, stream the blog generation process
            if tools and "blogs" in tools:
                try:
                    from app.tools.blogs.graph import app as blog_app
                    
                    blog_state = {
                        "topic": message,
                        "as_of": date.today().isoformat(),
                    }
                    
                    for event in blog_app.stream(blog_state, stream_mode="updates"):
                        for node_name, node_output in event.items():
                            # Stream progress updates for different nodes
                            if node_name == "router":
                                yield {
                                    "content": f"✓ Routing complete - Mode: {node_output.get('mode', 'unknown')}",
                                    "message_type": "progress",
                                    "node": "router"
                                }
                            elif node_name == "research":
                                evidence_count = len(node_output.get('evidence', []))
                                yield {
                                    "content": f"✓ Research complete - Found {evidence_count} sources",
                                    "message_type": "progress",
                                    "node": "research"
                                }
                            elif node_name == "orchestrator":
                                plan = node_output.get('plan')
                                if plan:
                                    yield {
                                        "content": f"✓ Planning complete - {len(plan.tasks)} sections planned",
                                        "message_type": "progress",
                                        "node": "orchestrator"
                                    }
                            elif node_name == "worker":
                                yield {
                                    "content": "✓ Section written",
                                    "message_type": "progress",
                                    "node": "worker"
                                }
                            elif node_name == "reducer":
                                if 'final' in node_output:
                                    yield {
                                        "content": node_output['final'],
                                        "message_type": "ai",
                                        "node": "final"
                                    }
                    
                    # Update thread timestamp
                    touch_thread(thread_id)
                    return
                except Exception as blog_error:
                    error_msg = str(blog_error)
                    print(f"Error streaming blog tool: {error_msg}")
                    
                    # Provide user-friendly error messages
                    if "name resolution failed" in error_msg or "503" in error_msg:
                        yield {
                            "content": "⚠️ **Blog Generation Failed**\n\nThe blog generation service is currently unavailable (network connection issue). This could be due to:\n- External API service is down\n- Network connectivity issues\n- DNS resolution problems\n\nPlease try again later or use the regular chat without the blog tool.",
                            "message_type": "ai"
                        }
                    else:
                        yield {
                            "content": f"⚠️ **Blog Generation Failed**\n\nAn error occurred while generating the blog:\n```\n{error_msg}\n```\n\nPlease try again or use the regular chat without the blog tool.",
                            "message_type": "ai"
                        }
                    return
            
            # Check if thread has a document
            doc_exists = has_document(thread_id)
            
            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [HumanMessage(content=message)],
                    "has_document": doc_exists,
                    "thread_id": thread_id
                },
                config=config,
                stream_mode="messages",
            ):
                # Only yield AI messages with content (skip tool messages and empty AI messages)
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield {
                        "content": message_chunk.content,
                        "message_type": "ai",
                        "tool_name": None
                    }
                # Skip ToolMessage and HumanMessage in stream (already displayed by frontend)
        except Exception as e:
            print(f"Error streaming message: {e}")
            raise Exception(f"Failed to stream message: {str(e)}")
    
    @staticmethod
    def update_thread_title(thread_id: str, title: str) -> bool:
        """Update the title for a thread"""
        try:
            save_thread_title(thread_id, title)
            return True
        except Exception as e:
            print(f"Error updating title: {e}")
            return False
    
    @staticmethod
    def delete_thread(thread_id: str) -> bool:
        """Delete a thread and all its associated data"""
        from app.database import DatabaseConfig, ThreadMetadata, DocumentMetadata, Checkpoint, CheckpointWrite
        from app.services.rag import _thread_paths
        import os
        
        session = DatabaseConfig.get_session_factory()()
        try:
            # Delete from database tables (cascade will handle related records)
            
            # Delete checkpoints and checkpoint writes
            session.query(CheckpointWrite).filter_by(thread_id=thread_id).delete()
            session.query(Checkpoint).filter_by(thread_id=thread_id).delete()
            
            # Delete document metadata (this should cascade from thread_metadata but let's be explicit)
            session.query(DocumentMetadata).filter_by(thread_id=thread_id).delete()
            
            # Delete thread metadata
            session.query(ThreadMetadata).filter_by(thread_id=thread_id).delete()
            
            session.commit()
            
            # Clean up storage files (PDF and metadata JSON)
            try:
                pdf_path, meta_path = _thread_paths(thread_id)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    print(f"Deleted PDF file: {pdf_path}")
                if os.path.exists(meta_path):
                    os.remove(meta_path)
                    print(f"Deleted metadata file: {meta_path}")
            except Exception as e:
                print(f"Warning: Failed to delete storage files for thread {thread_id}: {e}")
                # Don't fail the whole operation if file cleanup fails
            
            # Clear any in-memory caches
            try:
                from app.services.rag import _THREAD_RETRIEVERS, _THREAD_METADATA
                if thread_id in _THREAD_RETRIEVERS:
                    del _THREAD_RETRIEVERS[thread_id]
                if thread_id in _THREAD_METADATA:
                    del _THREAD_METADATA[thread_id]
            except Exception as e:
                print(f"Warning: Failed to clear thread cache for {thread_id}: {e}")
            
            print(f"Successfully deleted thread: {thread_id}")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error deleting thread {thread_id}: {e}")
            return False
        finally:
            session.close()
