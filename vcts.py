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
import logging
import logging.config
from os import path
import time
import json

from trade import vcts_trade

##################################################
# constant

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

# vcts_trade,VctsTrade
vctstrade  = vcts_trade.VctsTrade()

##################################################
# biz function

def continueGrowsChoice():
     # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    columns = ['opening_price','trade_price']
    best = vctstrade.getChoiceGrowsMarkets(columns,2,3,3,3)
    # for b in best:
    #     print(b)
    
    # print(vctstrade.getMarkets())

    while True:
        data_json =  vctstrade.getTickerMarkets(best)
        for data in data_json:   
            # print(json.dumps(data, indent=4, sort_keys=True))
            print('%10s' % data.get('market')
            ,'market-name'
            ,data.get('trade_time_kst')
            ,data.get('change')
            ,'%20f' % data.get('trade_price')
            ,'%20f' % data.get('change_price'))         
        print('-----------------------')
        time.sleep(3) 
        print('-----------------------')
        # market	종목 구분 코드	String
        # trade_date	최근 거래 일자(UTC)	String
        # trade_time	최근 거래 시각(UTC)	String
        # trade_date_kst	최근 거래 일자(KST)	String
        # trade_time_kst	최근 거래 시각(KST)	String
        # opening_price	시가	Double
        # high_price	고가	Double
        # low_price	저가	Double
        # trade_price	종가	Double
        # prev_closing_price	전일 종가	Double
        # change	EVEN : 보합  RISE : 상승  FALL : 하락	String
        # change_price	변화액의 절대값	Double
        # change_rate	변화율의 절대값	Double
        # signed_change_price	부호가 있는 변화액	Double
        # signed_change_rate	부호가 있는 변화율	Double
        # trade_volume	가장 최근 거래량	Double
        # acc_trade_price	누적 거래대금(UTC 0시 기준)	Double
        # acc_trade_price_24h	24시간 누적 거래대금	Double
        # acc_trade_volume	누적 거래량(UTC 0시 기준)	Double
        # acc_trade_volume_24h	24시간 누적 거래량	Double
        # highest_52_week_price	52주 신고가	Double
        # highest_52_week_date	52주 신고가 달성일	String
        # lowest_52_week_price	52주 신저가	Double
        # lowest_52_week_date	52주 신저가 달성일	String
        # timestamp	타임스탬프	Long

#################################################
# main
if __name__ == '__main__':
    continueGrowsChoice()
    # get candles chart data &  save to db
    # vtrade.loadMarketsCandlesMwdData()
    
    #scheduler = BlockingScheduler()
    #scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)

    

    




  