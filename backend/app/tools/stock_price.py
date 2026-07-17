import os
from langchain_core.tools import tool 
import requests
stock_api= os.getenv("STOCK_API_KEY")

@tool
def Stock_price(symbol: str):

    """fetch latest stock price for a given symbol (e.g. "AAPL", "TSLA")"""

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={stock_api}'
    r = requests.get(url)
    data = r.json()
    return data
