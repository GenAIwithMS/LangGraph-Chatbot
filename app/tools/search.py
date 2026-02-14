from langchain_community.tools import BraveSearch
import os
from dotenv import load_dotenv
load_dotenv()

brave_api = os.getenv("BRAVE_API_KEY")

Search = BraveSearch.from_api_key(api_key=brave_api)



