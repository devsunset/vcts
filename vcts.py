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

from trade import candles_mwd_data

##################################################
# constant

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

# candles_mwd_data
cmwd  = candles_mwd_data.MarketMonthWeekDayData()

##################################################
# biz function

#################################################
# main
if __name__ == '__main__':
    # 1.get candles chart data &  save to db
    # cmwd.load_candles_mwd_data()
    
    # 2.get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    columns = ['opening_price','trade_price']
    best = cmwd.getChoiceGrowsMarkets(columns,2,2,2,3)
    # for b in best:
    #     print(b)

    while True:
        data_json =  cmwd.getTickerMarkets(best)
        print(data_json)
        for data in data_json:   
            print(json.dumps(data, indent=4, sort_keys=True))
            break
            # print(data.get('market'),data.get('trade_date_kst'),data.get('trade_time_kst'),data.get('change'),data.get('trade_price'),data.get('change_price'))
        print('-----------------------')
        break
        time.sleep(3) 

    #scheduler = BlockingScheduler()
    #scheduler.add_job(main_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)

    

    




  