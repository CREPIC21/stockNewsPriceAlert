import requests
import datetime
import os
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

MY_NEWS_API = os.environ["MY_NEWS_API"]
# URL for news articles regarding particular stock
news_api_url = "https://newsapi.org/v2/everything"
news_param = {
        "q": COMPANY_NAME,
        "apiKey": MY_NEWS_API,
    }

STOCK_API = os.environ["MY_STOCK_API"]
# URL for checking the price charts increase/decrease of stock
stock_api_url = "https://www.alphavantage.co/query"
param_stock = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": STOCK_API
    }

# Getting today's date, month, year and index of the day in the week
today_date = datetime.datetime.now().day
index_today_date = datetime.datetime.now().strftime("%w")
year = datetime.datetime.now().year
month = datetime.datetime.now().month
print(today_date, year, month, index_today_date)


# Function for sending text message
def send_sms(msg):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    my_phone_number = os.environ["MY_PHONE_NUMBER"]
    my_twilio_phone_number = os.environ["MY_TWILIO_PHONE_NUMBER"]
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"TSLA: {msg}%.\n{news}",
        from_=my_twilio_phone_number,
        to=my_phone_number
    )
    print(message.status)


# Checking if the stock price for Tesla stock increased/decreased by 5% between yesterday and the day before yesterday
response = requests.get(url=stock_api_url, params=param_stock)
response.raise_for_status()
data = response.json()
print(data)
# if index of day in the week is 0, 1, or 2 then we know it was the weekend and the market was closed as we are only comparing yesterday and day before yesterday
# we will compare: thu-mon, wed-thu, thur-wed, fri-thur
if index_today_date != "0" and index_today_date != "1" and index_today_date != "2":
    if 1 <= today_date <= 9 and 1 <= month <= 9:
        stock_price_yesterday = round(float(data["Time Series (Daily)"][f"{year}-0{month}-0{today_date - 1}"]["4. close"]))
        stock_price_before_yesterday = round(float(data["Time Series (Daily)"][f"{year}-0{month}-0{today_date - 2}"]["4. close"]))
    elif 1 <= today_date <= 9:
        stock_price_yesterday = round(float(data["Time Series (Daily)"][f"{year}-{month}-0{today_date - 1}"]["4. close"]))
        stock_price_before_yesterday = round(float(data["Time Series (Daily)"][f"{year}-{month}-0{today_date - 2}"]["4. close"]))
    elif 1 <= month <= 9:
        stock_price_yesterday = round(float(data["Time Series (Daily)"][f"{year}-0{month}-{today_date - 1}"]["4. close"]))
        stock_price_before_yesterday = round(float(data["Time Series (Daily)"][f"{year}-0{month}-{today_date - 2}"]["4. close"]))
    else:
        stock_price_yesterday = round(float(data["Time Series (Daily)"][f"{year}-{month}-{today_date - 1}"]["4. close"]))
        stock_price_before_yesterday = round(float(data["Time Series (Daily)"][f"{year}-{month}-{today_date - 2}"]["4. close"]))
    price_difference = round(((stock_price_yesterday - stock_price_before_yesterday) / stock_price_yesterday) * 100)
    print(stock_price_yesterday)
    print(stock_price_before_yesterday)
    print(price_difference)


    # checking if the price difference increased/decreased for 5%, if yes then we are getting newest news articles relevant for that price change
    if price_difference >= 5 or price_difference <= 0:
        news = ""
        news_response = requests.get(url=news_api_url, params=news_param)
        news_response.raise_for_status()
        news_data = news_response.json()
        # getting three articles regarding stock price change
        for i in range(0, 3):
            article = news_data["articles"][i]["title"]
            print(article)
            news += "Article: " + article + "\n"
        print(news)

    # Sending a text message with the percentage change and each article's title regarding to price change to my phone number.
        if price_difference < 5:
            price_difference = str(price_difference).replace("-", "")
            sign = f" 🔻 DOWN FOR : {price_difference}"
            send_sms(sign)
        else:
            sign = f" 🔺 UP FOR : {price_difference}"
            send_sms(sign)
else:
    print("No news today, it is the weekend.")



