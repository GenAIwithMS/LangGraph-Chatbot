from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .database_backend import chatbot, Retrieve_all_threads, save_thread_title, get_all_thread_metadata
from langchain_core.messages import HumanMessage
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None

class TitleRequest(BaseModel):
    title: str

@app.post("/chat")
async def chat(request: ChatRequest):
    thread_id = request.thread_id
    if not thread_id:
        thread_id = str(uuid.uuid4())
        
    config = {"configurable": {"thread_id": thread_id}}
    
    input_message = HumanMessage(content=request.message)
    
    # Invoke the graph
    # The graph state has 'messages' key.
    final_state = chatbot.invoke({"messages": [input_message]}, config=config)
    
    messages = final_state["messages"]
    last_message = messages[-1]
    
    return {
        "response": last_message.content,
        "thread_id": thread_id
    }

@app.get("/threads")
async def get_threads():
    threads_ids = Retrieve_all_threads()
    metadata = get_all_thread_metadata()
    
    results = []
    for tid in threads_ids:
        title = metadata.get(tid, "New Chat")
        results.append({"thread_id": tid, "title": title})
    
    # Sort by some criteria if possible, but for now just return list
    return results

@app.get("/threads/{thread_id}")
async def get_thread_history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = chatbot.get_state(config)
        if not state.values:
            return []
        messages = state.values.get("messages", [])
        return [
            {
                "content": m.content,
                "type": m.type
            } for m in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Thread not found")


@app.post("/threads/{thread_id}/title")
async def update_title(thread_id: str, request: TitleRequest):
    save_thread_title(thread_id, request.title)
    return {"status": "success"}

@app.get("/health")
async def health():
    return {"status": "ok"}
