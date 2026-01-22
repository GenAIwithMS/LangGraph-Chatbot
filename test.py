# from thread_id_name import generate_id_name, model, structured_model
# prompt = "Create a chat title in 5 words or fewer. Title only. Question: Why use LangChain?"
# llm = structured_model.invoke(prompt)
# print(type(llm), repr(llm))
# raw = model.invoke(prompt)
# print(type(raw), repr(raw))
# import requests
from all_tools import weather,search,calculator,stock_price

weather_data = weather("lahore")
print(weather_data)

# # search_tool = search()
# calculator_tool = stock_price("AAPL")

# print(calculator_tool)

# url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"
#     # try:
# answer = requests.get(url)
# data = answer.json()
#     return data