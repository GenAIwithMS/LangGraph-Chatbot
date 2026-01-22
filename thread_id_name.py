from pydantic import BaseModel, Field
# from langchain_groq import ChatGroq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import uuid
load_dotenv()

model = ChatGroq(model="qwen/qwen3-32b")

class StructuredModel(BaseModel):
    title: str = Field(description="A short chat title (<= 5 words).")

structured_model = model.with_structured_output(StructuredModel)

def generate_id_name(question: str):
   
    prompt = f"""
    Create a chat title in 5 words or fewer.
    Title only, no explanation.
    Question: {question}
    """

    try:
        llm = structured_model.invoke(prompt)
        # if llm and getattr(llm, "title", None):
        #     return llm.title
        if llm and hasattr(llm, "title") and llm.title:
            return llm.title
    except Exception as e:
        print("STRUCTURED PARSE ERROR:", e)

    # fallback to raw text
    raw = model.invoke(prompt)
    return raw.content.strip()

def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

# thread_id = generate_thread_id()

# def access(message):
#     name = generate_id_name(message)
#     dic = {thread_id: name}
#     return dic

def generate_thread_title(message: str):
    """Generate a thread title from a message without circular dependencies"""
    name = generate_id_name(message)
    thread_id = generate_thread_id()
    return {thread_id: name}

# massage = "tell me about Langchain and why we use them"

# number = access(massage)
# value = list(number.values())[0]
# print(number)
# print(structured_model)