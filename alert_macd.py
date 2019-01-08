#!/usr/bin/env python

import logging
import pandas as pd
from datetime import datetime, timedelta
import time
import requests
import json

logging.basicConfig(filename='alert_macd.log',level=logging.DEBUG)

### FUNCTIONS ###

def get_url(url):
 response = requests.get(url)
 content = response.content.decode("utf8")
 return content

def send_message(text, chat_id):
 url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
 get_url(url)

# MACD indicator
def macd(df) :
 df['macd'] = df['C'].ewm(span=12, adjust=False).mean() - df['C'].ewm(span=26, adjust=False).mean()
 df['signal'] =  df['macd'].ewm(span=9, adjust=False).mean()
 print df
 return df

def GetMarket() :
 #get historical market data
 URL = "https://bittrex.com/Api/v2.0/pub/market/GetTicks"
 market = "BTC-ETH"
 interval = "fiveMin"
 timestamp = "1500915289433"
 PARAMS = {'marketName':market, 'tickInterval':interval, '_':timestamp}
 r = requests.get(url = URL, params = PARAMS)
 data = r.json()

 #convert data to pandas dataframe
 df = pd.DataFrame(data['result'])
 df.index.name = 'Index'
 return df


### MAIN CODE ###

TOKEN = "insert your token here"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
chatID = "insert your chat id here"

shouldRun = True
if datetime.now().minute not in {0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}:
 shouldRun = False

while True:
 if shouldRun == False:
  current_time = datetime.now()
  seconds = 60 - current_time.second
  minutes = current_time.minute + 1
  snooze = ((5 - minutes%5) * 60) + seconds
  logging.info('minutes:%s seconds:%s sleep:%s', minutes, seconds, snooze)
  localtime = time.asctime( time.localtime(time.time()))
  logging.info('sleeping at %s', localtime)
  time.sleep(snooze)  # Sleep until next quarter hour.
  shouldRun = True
 else:
  localtime = time.asctime( time.localtime(time.time()))
  logging.info("time to check market... wait for 2 minutes before begin...")
  time.sleep(60) #wait for 60 sec before run code

  df = GetMarket()
  df_macd = macd(df)

  if (
       df_macd['macd'].iloc[-1] > df_macd['signal'].iloc[-1] and
       df_macd['signal'].iloc[-2] > df_macd['macd'].iloc[-2]
  ):
   logging.info('ALERT TO END USER! >>> macd:%s signal:%s',  df_macd['macd'].iloc[-1], df_macd['signal'].iloc[-1])
   send_message("MACD ALERT! >>> macd={} signal={}".format( df_macd['macd'].iloc[-1], df_macd['signal'].iloc[-1]), chatID)
  else:
   logging.info('macd:%s signal:%s',  df_macd['macd'].iloc[-1], df_macd['signal'].iloc[-1])

  shouldRun = False

