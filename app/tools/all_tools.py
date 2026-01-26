import requests
from langchain_core.tools import tool 
from langchain_community.tools import BraveSearch
import os

brave_api = os.getenv("BRAVE_API_KEY")
weather_api= os.getenv("WEATHER_API_KEY")
stock_api= os.getenv("STOCK_API_KEY")

search = BraveSearch.from_api_key(api_key=brave_api)

@tool
def stock_price(symbol: str):

    """fetch latest stock price for a given symbol (e.g. "AAPL", "TSLA")"""

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={stock_api}'
    r = requests.get(url)
    data = r.json()
    return data

@tool
def calculator(first_num, second_num, evaluator):
    """Performe basic arthematic opration between two numbers"""
    return eval(f"{first_num} {evaluator} {second_num}")

@tool
def weather(city: str):
    """Use this tool to fetch the current weather conditions for any city. It provides real-time data including temperature, humidity, and a short description of the weather (e.g., clear sky, rain, snow)"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"
    # try:
    answer = requests.get(url)
    data = answer.json()
    return data

