from dotenv import load_dotenv
from langsmith import traceable
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from app.tools import Search, Weather, Calculator, Stock_price
from app.services.rag import has_document, retrieve_from_document
from app.database import DatabaseConfig, SQLiteCheckpointSaver, ThreadMetadata
import os

load_dotenv()

api = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=api
    )

# Available tools for the chatbot
all_tools = [Search, Weather, Calculator, Stock_price]


class Chatstate(TypedDict):
    """State definition for the chatbot"""
    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str
    has_document: bool


@traceable(name="My GPT")
def chat_node(state: Chatstate):
    """Main chat node that processes messages and uses tools"""
    messages = state["messages"]
    thread_id = state.get("thread_id")
    has_doc = state.get("has_document", False)
    
    # Only check document if state indicates one exists (optimization)
    if thread_id and has_doc:
        # Get the last user message to use as query
        last_user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_user_message = msg.content
                break
        
        # If we have a user message, retrieve relevant context from the document
        if last_user_message:
            try:
                retrieval_result = retrieve_from_document(last_user_message, thread_id)
                    # If retrieval was successful, prepend context to messages
                if "context" in retrieval_result and retrieval_result["context"]:
                    context_text = "\n\n".join(retrieval_result["context"])
                    context_message = SystemMessage(
                        content=f"""You have access to information from an uploaded document. Use this context to answer the user's question if relevant:

Document Context:
{context_text}

If the user's question is related to the document, base your answer on this context. If not related, answer normally using your knowledge or tools."""
                    )
                    # Insert context before the last user message
                    messages = list(messages[:-1]) + [context_message, messages[-1]]
            except Exception as e:
                print(f"Error retrieving document context: {e}")
    
    model_with_tools = model.bind_tools(all_tools)
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


# Create tool node
tool_node = ToolNode(all_tools)

# Build the state graph
graph = StateGraph(Chatstate)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

# Database checkpointer
check_pointer = SQLiteCheckpointSaver()

# Compile the chatbot with checkpointer
chatbot = graph.compile(checkpointer=check_pointer)

# In-memory checkpointer for temporary chats: nothing is ever written to the
# database, so temp conversations only live in the running process and are lost
# on refresh / new chat / backend restart.
memory_checkpointer = MemorySaver()
chatbot_memory = graph.compile(checkpointer=memory_checkpointer)

# Database session factory
Session = DatabaseConfig.get_session_factory()


# Thread management functions

def retrieve_all_threads(user_id: int | None = None):
    all_threads = set()
    try:
        for checkpoint_tuple in check_pointer.list(None):
            all_threads.add(checkpoint_tuple.config["configurable"]["thread_id"])
    except Exception as e:
        print(f"Error retrieving threads: {e}")
    return list(all_threads)


def save_thread_title(thread_id: str, title: str, user_id: int | None = None):
    session = Session()
    try:
        existing = session.query(ThreadMetadata).filter_by(thread_id=thread_id).first()
        if existing:
            existing.title = title
        else:
            new_thread = ThreadMetadata(thread_id=thread_id, title=title, user_id=user_id or 0)
            session.add(new_thread)
        session.commit()
    finally:
        session.close()


def touch_thread(thread_id: str):
    session = Session()
    try:
        existing = session.query(ThreadMetadata).filter_by(thread_id=thread_id).first()
        if existing:
            existing.title = existing.title
            session.commit()
    finally:
        session.close()


def get_thread_title_from_db(thread_id: str) -> str | None:
    session = Session()
    try:
        thread = session.query(ThreadMetadata).filter_by(thread_id=thread_id).first()
        return thread.title if thread else None
    finally:
        session.close()


def get_all_thread_metadata(user_id: int | None = None):
    session = Session()
    try:
        query = session.query(ThreadMetadata)
        if user_id:
            query = query.filter_by(user_id=user_id)
        threads = query.order_by(ThreadMetadata.updated_at.desc()).all()
        return {
            thread.thread_id: {
                "title": thread.title,
                "updated_at": thread.updated_at,
                "created_at": thread.created_at
            }
            for thread in threads
        }
    finally:
        session.close()
