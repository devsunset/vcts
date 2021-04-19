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

from pandas import DataFrame
import pandas as pd
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


pre_df = pd.DataFrame()

##################################################
# biz function

def monitorCoins(loop=False,looptime=3,sort='signed_change_rate',change=None, market=None, trade_price=None):
    best = []

    ### TYPE ONE
    markets = vctstrade.getMarkets()
    for i in markets.index:
        best.append(markets['market'][i])

    ### TYPE TWO
    # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    # columns = ['opening_price','trade_price']
    # best = vctstrade.getChoiceGrowsMarkets(columns,3,3,3,3)

    # TYPE THREE 
    # best.append('KRW-AERGO')
    # best.append('KRW-DOGE')

    ###########################################################################################

    while True:
        df = vctstrade.getTickerMarkets(best).sort_values(by=sort, ascending=False)

        global pre_df
        if len(pre_df) > 0:
            print('------------- compare')
   

        print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('%15s' % 'market'                
                ,'%7s' % 'change'
                ,'%12s' % '종가'
                ,'%13s' % '변화액'
                ,'%6s' % '변화율'
                ,'%11s' % '고가-종가'
                ,'%11s' % '고가-시가'
                ,'%11s' % '고가-저가'
                ,'%13s' % '시가'
                ,'%13s' % '저가'
                ,'%13s' % '고가'
                # ,'%7s' % '신고일'
                # ,'%12s' % '신고가'
                # ,'% 7s' % '신저일'
                # ,'%12s' % '신저가'
                ,'%23s' %  'market'
                )
        print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        for x in df.index:

            if change is not None:
                if change.find(df['change'][x]) == -1 :
                    continue

            if market is not None:
                tmp = df['market'][x]
                if tmp[:tmp.find('-')] not in market.split('|'):
                    continue

            if trade_price is not None:
                if int(df['trade_price'][x]) > 1000 :
                    continue

            print('%15s' % df['market'][x]
                ,'%6s' % df['change'][x]
                ,'%15f' % df['trade_price'][x]
                ,'%15f' % df['signed_change_price'][x]
                ,'%10f' % df['signed_change_rate'][x]
                ,'%15f' % (float(df['high_price'][x]) - float(df['trade_price'][x])) 
                ,'%15f' % (float(df['high_price'][x]) - float(df['opening_price'][x])) 
                ,'%15f' % (float(df['high_price'][x]) - float(df['low_price'][x])) 
                ,'%15f' % df['opening_price'][x]
                ,'%15f' % df['low_price'][x]
                ,'%15f' % df['high_price'][x]
                # ,'%10s' % df['highest_52_week_date'][x]
                # ,'%15f' % df['highest_52_week_price'][x]
                # ,'%10s' % df['lowest_52_week_date'][x]
                # ,'%15f' % df['lowest_52_week_price'][x]
                ,'%20s' % vctstrade.getMarketName(df['market'][x])
                )

        pre_df = df
                
        if(loop == True):
            time.sleep(looptime)
        else:
            break

    ###########################################################################################


#################################################
# main
if __name__ == '__main__':
    # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()
    
    # signed_change_rate 변화율
    # trade_volume	가장 최근 거래량	Double
    # acc_trade_price	누적 거래대금(UTC 0시 기준)	Double
    # acc_trade_price_24h	24시간 누적 거래대금	Double
    # acc_trade_volume	누적 거래량(UTC 0시 기준)	Double
    # acc_trade_volume_24h	24시간 누적 거래량	Double

    # monitorCoins(loop=False,looptime=3,sort='signed_change_rate',change='RISE',market='KRW',trade_price=1000)

    monitorCoins(loop=True,looptime=3,sort='signed_change_rate',market='KRW',trade_price=1000)

    #scheduler = BlockingScheduler()
    #scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)





    

    




  