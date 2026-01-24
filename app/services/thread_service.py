"""
Thread Service
Handles thread ID generation and title generation
"""

from pydantic import BaseModel, Field
# from langchain_groq import 
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import uuid
import os

load_dotenv()
api = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="openai/gpt-oss-120b", openai_api_key=api, base_url="https://api.canopywave.io/v1")


class StructuredModel(BaseModel):
    title: str = Field(description="A short chat title (<= 5 words).")


structured_model = model.with_structured_output(StructuredModel)


def generate_id_name(question: str):
    """Generate a short title from a question/message"""
    prompt = f"""
    Create a chat title in 5 words or fewer.
    Title only, no explanation.
    Question: {question}
    """

    try:
        llm = structured_model.invoke(prompt)
        if llm and hasattr(llm, "title") and llm.title:
            return llm.title
    except Exception as e:
        print("STRUCTURED PARSE ERROR:", e)

    # fallback to raw text
    raw = model.invoke(prompt)
    return raw.content.strip()


def generate_thread_id():
    """Generate a unique thread ID"""
    thread_id = str(uuid.uuid4())
    return thread_id


def generate_thread_title(message: str):
    """Generate a thread title from a message without circular dependencies"""
    name = generate_id_name(message)
    thread_id = generate_thread_id()
    return {thread_id: name}
