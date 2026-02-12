from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
api = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

llm = ChatOpenAI(model="xiaomimimo/mimo-v2-flash", api_key=api,base_url=base_url)
