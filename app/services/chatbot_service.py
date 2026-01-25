import sqlite3
from dotenv import load_dotenv
from langsmith import traceable
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.tools.all_tools import search, weather, calculator, stock_price
from app.services.rag_service import has_document, retrieve_from_document
import os

load_dotenv()

api = os.getenv("OPENAI_API_KEY")



model = ChatOpenAI(model="openai/gpt-oss-120b", openai_api_key=api, base_url="https://api.canopywave.io/v1")

# Available tools for the chatbot
all_tools = [search, weather, calculator, stock_price]


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

# Database connection and checkpointer
connection = sqlite3.connect(database="chatbot.db", check_same_thread=False)
check_pointer = SqliteSaver(connection)

# Compile the chatbot with checkpointer
chatbot = graph.compile(checkpointer=check_pointer)

# Initialize thread metadata table
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS thread_metadata (
    thread_id TEXT PRIMARY KEY,
    title TEXT
)
""")
connection.commit()


# Thread management functions

def retrieve_all_threads():
    """Retrieve all thread IDs from the checkpointer"""
    all_threads = set()
    for checkpoint in check_pointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def save_thread_title(thread_id: str, title: str):
    """Save or update a thread's title in the database"""
    cursor.execute("""
    INSERT OR REPLACE INTO thread_metadata (thread_id, title)
    VALUES (?, ?)
    """, (thread_id, title))
    connection.commit()


def get_thread_title_from_db(thread_id: str) -> str | None:
    """Get a thread's title from the database"""
    cursor.execute("SELECT title FROM thread_metadata WHERE thread_id=?", (thread_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_all_thread_metadata():
    """Get all thread IDs and their titles as a dictionary"""
    cursor.execute("SELECT thread_id, title FROM thread_metadata")
    return dict(cursor.fetchall())
