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

    while True:
        data_json =  vctstrade.getTickerMarkets(best)
        for data in data_json:   
            # print(json.dumps(data, indent=4, sort_keys=True))
            print(data.get('market'),data.get('trade_date_kst'),data.get('trade_time_kst'),data.get('change'),data.get('trade_price'),data.get('change_price'))
        print('-----------------------')
        time.sleep(3) 


    # "acc_trade_price": 79.84965309725581,
    # "acc_trade_price_24h": 82.44701511,
    # "acc_trade_volume": 28548413.13348581,
    # "acc_trade_volume_24h": 29539273.44148463,
    # "change": "RISE",
    # "change_price": 2.7e-07,
    # "change_rate": 0.1050583658,
    # "high_price": 3.1e-06,
    # "highest_52_week_date": "2021-04-14",
    # "highest_52_week_price": 3.1e-06,
    # "low_price": 2.48e-06,
    # "lowest_52_week_date": "2021-01-03",
    # "lowest_52_week_price": 4.5e-07,
    # "market": "BTC-BFC",
    # "opening_price": 2.59e-06,
    # "prev_closing_price": 2.57e-06,
    # "signed_change_price": 2.7e-07,
    # "signed_change_rate": 0.1050583658,
    # "timestamp": 1618440819083,
    # "trade_date": "20210414",
    # "trade_date_kst": "20210415",
    # "trade_price": 2.84e-06,
    # "trade_time": "225338",
    # "trade_time_kst": "075338",
    # "trade_timestamp": 1618440818000,
    # "trade_volume": 2339.80503287



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

    

    




  