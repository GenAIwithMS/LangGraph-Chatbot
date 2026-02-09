from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
api = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
groq_api = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-120b",api_key= groq_api)
# llm_config = {"model": "openai/gpt-oss-120b"}
# if base_url:
# 	llm_config["base_url"] = base_url
# llm = ChatOpenAI(model="openai/gpt-oss-120b", api_key=api, base_url=base_url)
