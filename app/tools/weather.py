from langchain_core.tools import tool
import requests
import os

weather_api= os.getenv("WEATHER_API_KEY")

@tool
def Weather(city: str):
    """Use this tool to fetch the current weather conditions for any city. It provides real-time data including temperature, humidity, and a short description of the weather (e.g., clear sky, rain, snow)"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"
    # try:
    answer = requests.get(url)
    data = answer.json()
    return data
