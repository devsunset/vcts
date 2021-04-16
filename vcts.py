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

def monitorCoins():
     # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    columns = ['opening_price','trade_price']
    best = vctstrade.getChoiceGrowsMarkets(columns,2,3,3,3)
    # for b in best:
    #     print(b)
    # print(vctstrade.getMarkets())
        
    print(vctstrade.getTickerMarkets(best).sort_values(by='signed_change_rate', ascending=False))
#     while True:
#         data_json =  vctstrade.getTickerMarkets(best)
#         print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
#         print('%15s' % 'market-name'                
#                 ,'%20s' % 'change'
#                 ,'%13s' % '종가'
#                 ,'%10s' % '변화액'
#                 ,'%10s' % '변화율'
#                 ,'%10s' % '전일 종가'
#                 ,'%13s' % '시가'
#                 ,'%13s' % '저가'
#                 ,'%13s' % '고가'
#                 ,'%7s' % '신고일'
#                 ,'%15s' % '신고가'
#                 ,'% 7s' % '신저일'
#                 ,'%15s' % '신저가'
#                 )
#         print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
#         # vctstrade.getMarketName(data.get('market')
#         for data in data_json:   
#             # print(json.dumps(data, indent=4, sort_keys=True))
#             print('%10s' % data.get('market')
#                 #,'% 1s' % vctstrade.getMarketName(data.get('market'))
#                 ,'%10s' % data.get('change')
#                 ,'%15f' % data.get('trade_price')
#                 ,'%15f' % data.get('signed_change_price')
#                 ,'%10f' % data.get('signed_change_rate')
#                 ,'%15f' % data.get('prev_closing_price')
#                 ,'%15f' % data.get('opening_price')
#                 ,'%15f' % data.get('low_price')
#                 ,'%15f' % data.get('high_price')
#                 ,'%10s' % data.get('highest_52_week_date')
#                 ,'%15f' % data.get('highest_52_week_price')
#                 ,'%10s' % data.get('lowest_52_week_date')
#                 ,'%15f' % data.get('lowest_52_week_price')
#                 )
#         time.sleep(10) 

#################################################
# main
if __name__ == '__main__':
       # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()

    monitorCoins()

    #scheduler = BlockingScheduler()
    #scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)

    

    




  