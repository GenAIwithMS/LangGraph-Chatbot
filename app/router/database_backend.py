import sqlite3
from dotenv import load_dotenv
from langsmith import traceable
from langchain_groq import ChatGroq
from typing import TypedDict , Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph , START , END
from langgraph.prebuilt import ToolNode,tools_condition
from rag_backend import rag_tool
from app.tools.all_tools import search, weather, calculator, stock_price

load_dotenv()


model = ChatGroq(model="qwen/qwen3-32b")

all_tools = [search,weather,calculator,stock_price]

class Chatstate(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str  
    has_document: bool


def generate_id_name(question : str):
    pass
    

@traceable(name="My GPT")
def chat_node(state: Chatstate):
    messages = state["messages"]
    model_with_tools = model.bind_tools(all_tools)
    
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(all_tools)

graph = StateGraph(Chatstate)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools", "chat_node")

connection = sqlite3.connect(database="chatbot.db", check_same_thread=False)

check_pointer = SqliteSaver(connection)

chatbot = graph.compile(checkpointer=check_pointer)


def Retrieve_all_threads():

    all_threads = set()

    for checkpoint in check_pointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)



cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS thread_metadata (
    thread_id TEXT PRIMARY KEY,
    title TEXT
)
""")
connection.commit()


def save_thread_title(thread_id: str, title: str):
    cursor.execute("""
    INSERT OR REPLACE INTO thread_metadata (thread_id, title)
    VALUES (?, ?)
    """, (thread_id, title))
    connection.commit()


def get_thread_title_from_db(thread_id: str) -> str | None:
    cursor.execute("SELECT title FROM thread_metadata WHERE thread_id=?", (thread_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_all_thread_metadata():
    cursor.execute("SELECT thread_id, title FROM thread_metadata")
    return dict(cursor.fetchall())
