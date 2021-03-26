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

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

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
    #scheduler.add_job(main_process, 'interval', seconds=config.INTERVAL_SECONDS)

    # main_process()

    #try:
    #    scheduler.start()
    #except Exception as err:
    #    print(err)


    
    # upbitapi  API TEST 
    ###############################################################
    upbitapi = upbitapi.UpbitApi(config.ACCESS_KEY,config.SECRET)

    # QUOTATION API TEST 
    ###############################################################    
    # print('■■■■■■■■■■ - QUOTATION API - 시세 종목 조회 - 마켓 코드 조회 : getQuotationMarketAll()')
    # print(upbitapi.getQuotationMarketAll())

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들 : getQuotationCandlesMinutes(1,"KRW-BTC")')
    # print(upbitapi.getQuotationCandlesMinutes(1,'KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 일(Day) 캔들 : getQuotationCandlesDays("KRW-BTC")')
    # print(upbitapi.getQuotationCandlesDays('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 주(Week) 캔들 : getQuotationCandlesWeeks("KRW-BTC")')
    # print(upbitapi.getQuotationCandlesWeeks('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 월(Month) 캔들 : getQuotationCandlesMonths("KRW-BTC")')
    # print(upbitapi.getQuotationCandlesMonths('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 체결 조회 - 최근 체결 내역 : getQuotationTradesTicks("KRW-BTC")')
    # print(upbitapi.getQuotationTradesTicks('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 Ticker 조회 - 현재가 정보 : getQuotationTicker(["KRW-BTC","KRW-ETH"])')
    # print(upbitapi.getQuotationTicker(['KRW-BTC','KRW-ETH']))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 호가 정보(Orderbook) 조회 - 호가 정보 조회 : getQuotationOrderbook(["KRW-BTC","KRW-ETH"])')
    # print(upbitapi.getQuotationOrderbook(['KRW-BTC','KRW-ETH']))

    # EXCHANGE API TEST 
    ###############################################################    
    # print('■■■■■■■■■■ - EXCHANGE API - 자산 - 전체 계좌 조회 : getExchangeAccounts()')
    # print(upbitapi.getExchangeAccounts())

    # print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문 가능 정보 : getExchangeOrdersChance()')
    # print(upbitapi.getExchangeOrdersChance('KRW-BTC'))

    print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문 가능 정보 : getExchangeOrdersChance()')
    print(upbitapi.getExchangeOrdersChance('KRW-BTC'))

    # print('■■■■■■■■■■ - 요청 수 제한')
    # print(upbitapi.getRemainingReq())