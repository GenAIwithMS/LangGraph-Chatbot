from typing import Optional, List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.services.chatbot_service import (
    chatbot,
    retrieve_all_threads,
    save_thread_title,
    get_thread_title_from_db,
    get_all_thread_metadata
)
from app.services.thread_service import generate_thread_id, generate_id_name


class ChatService:
    """Service class to handle chat-related business logic"""
    
    @staticmethod
    def create_new_thread() -> str:
        """Create a new thread and return its ID"""
        thread_id = generate_thread_id()
        # Initialize with default title
        save_thread_title(thread_id, "New Chat")
        return thread_id
    
    @staticmethod
    def get_or_create_thread_title(thread_id: str, user_message: Optional[str] = None) -> str:
        """
        Get thread title from DB or generate new one from user message.
        Maintains the same logic as the Streamlit frontend.
        """
        # Try to fetch from DB first
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
        """
        Retrieve all threads with their titles.
        Returns list of dicts with thread_id and title.
        """
        thread_ids = retrieve_all_threads()
        metadata = get_all_thread_metadata()
        
        threads = []
        for tid in thread_ids:
            title = metadata.get(tid, "New Chat")
            threads.append({
                "thread_id": tid,
                "title": title
            })
        
        return threads
    
    @staticmethod
    def load_conversation(thread_id: str) -> List[Dict[str, str]]:
        """
        Load conversation history for a thread.
        Returns messages in format compatible with frontend.
        """
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
                    formatted_messages.append({
                        "content": message.content,
                        "type": "ai"
                    })
                elif isinstance(message, ToolMessage):
                    formatted_messages.append({
                        "content": message.content,
                        "type": "tool"
                    })
            
            return formatted_messages
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []
    
    @staticmethod
    def send_message(message: str, thread_id: str) -> Dict[str, Any]:
        """
        Send a message and get response.
        Maintains the same logic as the Streamlit frontend.
        """
        config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {"thread_id": thread_id}
        }
        
        try:
            # Invoke chatbot with user message
            final_state = chatbot.invoke(
                {"messages": [HumanMessage(content=message)]},
                config=config
            )
            
            messages = final_state["messages"]
            
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
    def stream_message(message: str, thread_id: str):
        """
        Stream message response.
        Yields chunks of the response as they arrive.
        """
        config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {"thread_id": thread_id}
        }
        
        try:
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="messages",
            ):
                # Yield different types of messages
                if isinstance(message_chunk, ToolMessage):
                    yield {
                        "content": message_chunk.content,
                        "message_type": "tool",
                        "tool_name": getattr(message_chunk, "name", "tool")
                    }
                elif isinstance(message_chunk, AIMessage):
                    yield {
                        "content": message_chunk.content,
                        "message_type": "ai",
                        "tool_name": None
                    }
                elif isinstance(message_chunk, HumanMessage):
                    yield {
                        "content": message_chunk.content,
                        "message_type": "human",
                        "tool_name": None
                    }
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
