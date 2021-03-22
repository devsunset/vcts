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

from common import constant
from common import common


##################################################
# constant

# target db
TARGET_DB = constant.TARGET_DB

##################################################
# biz function

# get market info save to db (vcts_meta table).
def getMarketSaveToDb():
    # Request  마켓 코드 조회
    url = "https://api.upbit.com/v1/market/all" 
    querystring = {"isDetails":"true"} 
    response = requests.request("GET", url, params=querystring) 
    market_dict = json.loads(response.text)
    
    # Response 
    # market         업비트에서 제공중인 시장 정보 String
    # korean_name    거래 대상 암호화폐 한글명String
    # english_name   거래 대상 암호화폐 영문명String
    # market_warning 유의 종목 여부 NONE (해당 사항 없음), CAUTION(투자유의) String
    try:
      conn = sqlite3.connect(TARGET_DB)

      try:
        sqlText = 'drop table vcts_meta'
        common.Common().executeTxDB(conn,sqlText)
      except Exception as err:
        pass

      sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name, market_warning)'
      common.Common().executeTxDB(conn,sqlText)
      
      for data in market_dict:
        #print(data)
        data.setdefault('market_warning','')
        sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning)'
        sqlText+= ' values ("'+data.get('market')+'","'+data.get('korean_name')+'","'+data.get('english_name')+'","'+data.get('market_warning')+'")'
        common.Common().executeTxDB(conn,sqlText)
    
      conn.commit()
      conn.close()
    except Exception as err:
      print(err)


# main process
def main_process():   
    print("hello world ---------------") 
    getMarketSaveToDb()

#################################################
# main
if __name__ == '__main__':
    #scheduler = BlockingScheduler()
    #scheduler.add_job(main_process, 'interval', seconds=stock_constant.INTERVAL_SECONDS)
    main_process()
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    print(err)


