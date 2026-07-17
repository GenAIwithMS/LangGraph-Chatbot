from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
# api = os.getenv("OPENAI_API_KEY")
# base_url = os.getenv("OPENAI_BASE_URL")

# llm = ChatOpenAI(model="moonshotai/kimi-k2.5", api_key=api)
llm = ChatGroq(model="qwen/qwen3-32b")