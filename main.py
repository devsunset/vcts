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

from apscheduler.schedulers.blocking import BlockingScheduler
import bs4
import json
import logging
import logging.config
from os import path
import requests
import sqlite3
import sys
from urllib.parse import urlencode

from common import config
from common import common
from upbitapi import upbitapi

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

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
      except Exception as e:
        logging.error(' Exception : %s' % e)

      sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name, market_warning)'
      common.executeTxDB(conn,sqlText)
      
      for data in market_dict:
        data.setdefault('market_warning','')
        sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning)'
        sqlText+= ' values ("'+data.get('market')+'","'+data.get('korean_name')+'","'+data.get('english_name')+'","'+data.get('market_warning')+'")'
        common.executeTxDB(conn,sqlText)
    
      conn.commit()
    except Exception as e:
      logging.error(' Exception : %s' % e)
    finally:
      if conn is not None:
        conn.close()


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
      
    