# -*- coding: utf-8 -*-
##################################################
#
#          virtual coin trade system
#
##################################################

##################################################
#
# 개요 - 프로세스 설명
#
##################################################

##################################################
# import

import sys
import sqlite3
import bs4
import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler

from common import config
from common import common
from upbitapi import upbitapi

from urllib.parse import urlencode

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

common = common.Common()
upbitapi = upbitapi.UpbitApi(config.ACCESS_KEY,config.SECRET)

##################################################
# biz function

# load market info save to db (vcts_meta table).
def loadMarketSaveToDb():
    market_dict = upbitapi.getQuotationMarketAll()

    try:
      conn = sqlite3.connect(TARGET_DB)

      try:
        sqlText = 'drop table vcts_meta'
        common.executeTxDB(conn,sqlText)
      except Exception as err:
        pass

      sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name, market_warning)'
      common.executeTxDB(conn,sqlText)
      
      for data in market_dict:
        #print(data)
        data.setdefault('market_warning','')
        sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning)'
        sqlText+= ' values ("'+data.get('market')+'","'+data.get('korean_name')+'","'+data.get('english_name')+'","'+data.get('market_warning')+'")'
        common.executeTxDB(conn,sqlText)
    
      conn.commit()
      conn.close()
    except Exception as err:
      print(err)

def getMarkets():
  df = common.searchDB("SELECT * FROM VCTS_META")
  print(df)

  for i in df.index:
    print(df['market'][i])


# main process
def main_process():   
    # loadMarketSaveToDb()
    getMarkets()    

#################################################
# main
if __name__ == '__main__':
    #scheduler = BlockingScheduler()
    #scheduler.add_job(main_process, 'interval', seconds=config.INTERVAL_SECONDS)

    main_process()

    #try:
    #    scheduler.start()
    #except Exception as err:
    #    print(err)
      
    