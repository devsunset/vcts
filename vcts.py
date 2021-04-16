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
    best = []
    ### TYPE ONE
    # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    # columns = ['opening_price','trade_price']
    # best = vctstrade.getChoiceGrowsMarkets(columns,2,3,3,3)
    # for b in best:
    #     print(b)
    
    ### TYPE TWO
    markets = vctstrade.getMarkets()
    for i in markets.index:
        # logger.warn(markets['market'][i]+" : "+markets['korean_name'][i])
        best.append(markets['market'][i])

    # TYPE THREE 
    # best.append('KRW-DOGE')

    ###########################################################################################

    df = vctstrade.getTickerMarkets(best).sort_values(by='signed_change_rate', ascending=False)

    while True:
        print('--------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('%15s' % 'market'                
                ,'%7s' % 'change'
                ,'%12s' % '종가'
                ,'%13s' % '변화액'
                ,'%6s' % '변화율'
                # ,'%10s' % '전일 종가'
                ,'%13s' % '시가'
                ,'%13s' % '저가'
                ,'%13s' % '고가'
                ,'%20s' %  'market'
                # ,'%7s' % '신고일'
                # ,'%15s' % '신고가'
                # ,'% 7s' % '신저일'
                # ,'%15s' % '신저가'
                )
        print('--------------------------------------------------------------------------------------------------------------------------------------------------------------')
        for x in df.index:
            if df['change'][x] != 'RISE' or str(df['market'][x])[0:4] != 'KRW-':
                continue

            print('%15s' % df['market'][x]
                ,'%6s' % df['change'][x]
                ,'%15f' % df['trade_price'][x]
                ,'%15f' % df['signed_change_price'][x]
                ,'%10f' % df['signed_change_rate'][x]
                # ,'%15f' % df['prev_closing_price'][x]
                ,'%15f' % df['opening_price'][x]
                ,'%15f' % df['low_price'][x]
                ,'%15f' % df['high_price'][x]
                ,'%20s' % vctstrade.getMarketName(df['market'][x])
                # ,'%10s' % df['highest_52_week_date'][x]
                # ,'%15f' % df['highest_52_week_price'][x]
                # ,'%10s' % df['lowest_52_week_date'][x]
                # ,'%15f' % df['lowest_52_week_price'][x]
                )
        break
        # time.sleep(5) 

    ###########################################################################################


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

    

    




  