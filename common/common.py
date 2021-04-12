# -*- coding: utf-8 -*-
##################################################
#
#                   common.py
#
##################################################

##################################################
# import

import bs4
from pandas import DataFrame
import datetime
import logging
import logging.config
import math
from os import path
import random
import requests
import sqlite3
import sys
import telegram
import unicodedata
import urllib3

from common import config
# import config

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

##################################################
# delcare

# telegram
bot = telegram.Bot(token=config.TELEGRAM_TOKEN)

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('camping-reservation')

##################################################

class Common():
    # search sql query - select
    def searchDB(self, sqlText, sqlParam=None, targetDB=TARGET_DB):
        columns = []
        result = []
        try:
            conn = sqlite3.connect(targetDB)
            cur = conn.cursor()
            sql = sqlText
            if sqlParam == None:
                cur.execute(sql)
            else:
              if str(type(sqlParam)) == "<class 'tuple'>":                    
                cur.execute(sql, sqlParam)
              else:
                cur.executemany(sql,sqlParam)
            columns = list(map(lambda x: x[0], cur.description))
            result = cur.fetchall()
            df = DataFrame.from_records(data=result, columns=columns)
        finally:
          if conn is not None:
            conn.close()
        return df

    # execute sql query - insert/update/delete
    def executeDB(self, sqlText, sqlParam=None, targetDB=TARGET_DB):
        try:
          conn = sqlite3.connect(targetDB)
          cur = conn.cursor()
          sql = sqlText
          if sqlParam == None:
              cur.execute(sql)
          else:
              if str(type(sqlParam)) == "<class 'tuple'>":    
                cur.execute(sql, sqlParam)
              else:
                cur.executemany(sql,sqlParam)
          conn.commit()
        finally:
          if conn is not None:
            conn.close()
        return cur.lastrowid

    # search sql query - select
    def searchTxDB(self, conn, sqlText, sqlParam=None):
        columns = []
        result = []
        try:
            cur = conn.cursor()
            sql = sqlText
            if sqlParam == None:
                cur.execute(sql)
            else:
                if str(type(sqlParam)) == "<class 'tuple'>":    
                    cur.execute(sql, sqlParam)
                else:
                    cur.executemany(sql,sqlParam)
            columns = list(map(lambda x: x[0], cur.description))
            result = cur.fetchall()
            df = DataFrame.from_records(data=result, columns=columns)
        return df

    # execute sql query - insert/update/delete
    def executeTxDB(self, conn, sqlText, sqlParam=None):
        try:
          cur = conn.cursor()
          sql = sqlText
          if sqlParam == None:
              cur.execute(sql)
          else:
             if str(type(sqlParam)) == "<class 'tuple'>":    
                cur.execute(sql, sqlParam)
             else:   
                cur.executemany(sql,sqlParam)
        return cur.lastrowid

    # telegram message send
    def send_telegram_msg(self, msg):
        try:
            # bot.deleteWebhook()
            # try:
            #     chat_id = bot.getUpdates()[-1].message.chat.id                
            # except Exception as e:
            #     chat_id = config.TELEGRAM_CHAT_ID
            # bot sendMessage
            bot.sendMessage(chat_id=config.TELEGRAM_CHAT_ID, text=msg)
            logger.warn(msg)
        except Exception as e:
            logger.error(' send_telegram_msg Exception : %s' % e)

    # log
    def log(self, msg, push_yn="Y"):
        if push_yn == 'Y':
            self.send_telegram_msg(msg)
            logger.warning(msg)
        else:
            logger.warning(msg)

    # crawling
    def getCrawling(self, url):
        html = ""
        try:
            resp = requests.get(url)
            html = resp.text
        except Exception as e:
            logger.error(' getCrawling Exception : %s' % e)
        return html

    # sert crawling
    def getSertCrawling(self, url, cookies=None):
        html = ""
        try:
            requests.packages.urllib3.disable_warnings()
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass

        try:
            resp = requests.get(url, cookies=cookies,verify=False)
            html = resp.text
        except Exception as e:
            logger.error(' getHttpsCrawling Exception : %s' % e)
        return html

##################################################
# main
if __name__ == '__main__':
    comm = Common()
    print('* send_telegram_msg : ', comm.send_telegram_msg(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : send_telegram_msg"))
    print()
    print('* log push_yn -> Y : ', comm.log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : Y", "Y"))
    print()
    print('* log push_yn -> N : ',  comm.log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : N", "N"))
    print()
    print('* getCrawling html : ', comm.getCrawling("https://devsunset.github.io/"))
    print()
    print('* getCrawling BeautifulSoup')
    html = comm.getCrawling("https://www.google.com/")
    bs = bs4.BeautifulSoup(html, 'html.parser')
    tags = bs.select('a')
    for i in range(len(tags)):
        txt = tags[i].get("href")
        print(txt)
