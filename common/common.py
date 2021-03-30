# -*- coding: utf-8 -*-
##################################################
#
#                   common 
#
##################################################

##################################################
# import

import sys
import sqlite3
import datetime
import math
import unicodedata
import random
import requests
import bs4
import telegram
from pandas import DataFrame

from common import config
# import config

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

##################################################
# delcare 

# telegram
bot = telegram.Bot(token = config.TELEGRAM_TOKEN)

##################################################
class Common():
    # search sql query - select 
    def searchDB(self,sqlText,sqlParam=None,targetDB=TARGET_DB):
        columns = []
        result = []
        conn = sqlite3.connect(targetDB)
        with conn:
         cur = conn.cursor()
         sql = sqlText
         if sqlParam == None:
           cur.execute(sql)
         else:
           cur.execute(sql,sqlParam)
        columns = list(map(lambda x: x[0], cur.description))
        result = cur.fetchall()            
        df = DataFrame.from_records(data=result, columns=columns)
        return df

    # execute sql query - insert/update/delete
    def executeDB(self,sqlText,sqlParam=None,targetDB=TARGET_DB):
        conn = sqlite3.connect(targetDB)
        cur = conn.cursor()
        sql = sqlText
        if sqlParam == None:
         cur.execute(sql)
        else:
         cur.execute(sql, sqlParam)
        conn.commit()        
        conn.close()
        return cur.lastrowid

    # search sql query - select 
    def searchTxDB(self,conn,sqlText,sqlParam=None):
        columns = []
        result = []
        with conn:
         cur = conn.cursor()
         sql = sqlText
         if sqlParam == None:
           cur.execute(sql)
         else:
           cur.execute(sql,sqlParam)
        columns = list(map(lambda x: x[0], cur.description))
        result = cur.fetchall()    
        df = DataFrame.from_records(data=result, columns=columns)
        return df

    # execute sql query - insert/update/delete
    def executeTxDB(self,conn,sqlText,sqlParam=None):
        cur = conn.cursor()
        sql = sqlText
        if sqlParam == None:
          cur.execute(sql)
        else:
          cur.execute(sql, sqlParam)
        return cur.lastrowid

    # telegram message send
    def send_telegram_msg(self,msg):
      try:
        bot.deleteWebhook()
        chat_id = bot.getUpdates()[-1].message.chat.id
        # bot sendMessage
        bot.sendMessage(chat_id = chat_id, text=msg)
      except Exception as err:
        print(err)

    # log 
    def log(self,msg,push_yn):
        if push_yn == 'Y' :
           self.send_telegram_msg(msg)
           print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : "+msg)
        else:
           print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : "+msg)
       
    # rpad 
    def rpad(self,input_s="", max_size=10, fill_char=" "):
        l = 0 
        for c in input_s:
         if unicodedata.east_asian_width(c) in ['F', 'W']:
          l+=2
         else: 
          l+=1
        return input_s+fill_char*(max_size-l)

    # crawling
    def getCrawling(self,url):
        resp = None    
        resp = requests.get(url)       
        html = resp.text
        return html

##################################################
# main     
     
if __name__=='__main__': 
   comm = Common()
   print('--- unit test start ---')
   print("")
   print('* db - db_init.py test skip')
   print('* send_telegram_msg : ',comm.send_telegram_msg(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : send_telegram_msg"))
   print('* log Y : ',comm.log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : Y","Y"))
   print('* log N : ',comm.log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : N","N"))
   print('* rpad : ',comm.rpad("1234",10,"0"))
   print('* getCrawling : ',comm.getCrawling("https://devsunset.github.io/"))
   html = comm.getCrawling("https://www.google.com/")
   bs = bs4.BeautifulSoup(html, 'html.parser')
   tags = bs.select('a') 
   for i in range(len(tags)):    
       txt = tags[i].get("href")
       print(txt)    
   print('--- unit test end ---')
