"""
Chatbot Service - LangGraph Setup and Database Management
Handles the core chatbot logic, LangGraph state management, and thread metadata
"""

import sqlite3
from dotenv import load_dotenv
from langsmith import traceable
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.tools.all_tools import search, weather, calculator, stock_price
import os

load_dotenv()

api = os.getenv("OPENAI_API_KEY")


# Initialize LLM model
# model = ChatGroq(model="qwen/qwen3-32b")
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
