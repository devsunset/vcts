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

import datetime
from pandas import DataFrame
import pandas as pd
import numpy as np
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

def monitorMarkets(loop=False, looptime=3, sort='signed_change_rate', change=None, market=None, trade_price=None):
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
    # best.append('KRW-DOGE')

    ###########################################################################################
    while True:
        df = vctstrade.getTickerMarkets(best).sort_values(by=sort, ascending=False)
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
        if(loop == True):
            time.sleep(looptime)
        else:
            break

def watchJumpMarkets(loop=False, looptime=3, period=7, market=None, trade_price=None):
        idx=0
        history_df =  pd.DataFrame()
        best = []
        # best.append('KRW-DOGE')

        fund_amount = 300000

        while True:
            if len(best) == 0:
                markets = vctstrade.getMarkets()
                for i in markets.index:
                    best.append(markets['market'][i])

            stand_df = pd.DataFrame(best, columns=['market'])

            df = vctstrade.getTickerMarkets(best).sort_values(by='signed_change_rate', ascending=False)
                        
            now_df =  pd.DataFrame(df, columns=['market','trade_price'])
            now_df[datetime.datetime.now().strftime("%H:%M:%S")] = now_df['trade_price']

            if len(history_df) == 0:
                history_df = pd.merge(stand_df, now_df, on = 'market')
            else:
                del history_df['trade_price']
                history_df = pd.merge(history_df, now_df, on = 'market')

            temp_headers = history_df.columns.tolist()
            
            headers  = []
            headers.append('market')
            headers.append('trade_price')
            for x in temp_headers:
                if x !='market' and x !='trade_price':
                    headers.append(x)

            history_df = history_df.reindex(columns=headers)
            
            if len (history_df.columns.tolist()) > period :
                del history_df[history_df.columns.tolist()[2]]

            analysis_df = history_df.copy()

            if len(history_df.columns.tolist()) == period:                
                for i in range(period-3):
                    analysis_df['diff_'+str(i+1)] = history_df[history_df.columns.tolist()[1]] - history_df[history_df.columns.tolist()[i+2]]

                for i in range(period-3):
                    analysis_df['rate_'+str(i+1)] =  (analysis_df['diff_'+str(i+1)] / history_df[history_df.columns.tolist()[1]]) * 100
                
                tdf = analysis_df.sort_values(by='rate_'+str(period-3), ascending=False)

                print('--->')

                buytarget = []
                amount = []
                for x in tdf.index:
                    if market is not None:
                        tmp = tdf['market'][x]
                        if tmp[:tmp.find('-')] not in market.split('|'):
                            continue

                    if trade_price is not None:
                        if int(tdf['trade_price'][x]) > 1000 :
                            continue
                    
                    if float(tdf['rate_1'][x]) < 4.5 :
                            continue

                    if float(tdf['rate_'+str(period-3)][x]) < 0.5 :
                            continue
                    
                    # print('%15s' % tdf['market'][x]
                    # ,'%15f' % tdf['trade_price'][x]
                    # ,'%15f' % tdf['diff_1'][x]
                    # ,'%15f' % tdf['rate_1'][x]
                    # ,'%15f' % tdf['diff_'+str(period-3)][x]
                    # ,'%15f' % tdf['rate_'+str(period-3)][x]
                    # ,'%20s' % vctstrade.getMarketName(tdf['market'][x])
                    # )

                    buytarget.append(tdf['market'][x])
                    amount.append(tdf['trade_price'][x])

                if len(buytarget) > 0 :
                     while True:
                        choice = buytarget[0:1]
                        df = vctstrade.getTickerMarkets(choice).sort_values(by='signed_change_rate', ascending=False)
                        buy_cnt = fund_amount/float(amount[0])
                        buy_amount = buy_cnt * float(amount[0])

                        if  (((float(df['trade_price'][x]) - float(amount[0])) /  float(amount[0]) ) * 100) > 5.55:
                            print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                            print('%15s' % 'market'                
                                    ,'%7s' % 'change'
                                    ,'%12s' % '종가'
                                    ,'%12s' % '시가'
                                    ,'%13s' % '변화액'
                                    ,'%6s' % '변화율'
                                    ,'%12s' % 'buy_cnt'
                                    ,'%17s' % 'amount'
                                    ,'%23s' %  'market'
                                    )
                            print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                            for x in df.index:
                                print('%15s' % df['market'][x]
                                    ,'%6s' % df['change'][x]
                                    ,'%15f' % df['trade_price'][x]
                                    ,'%15f' % amount[0]
                                    ,'%15f' % (float(df['trade_price'][x]) - float(amount[0]))
                                    ,'%10f' % (((float(df['trade_price'][x]) - float(amount[0])) /  float(amount[0]) ) * 100)
                                    ,'%15f' % buy_cnt
                                    ,'%15f' % (float(df['trade_price'][x]) * buy_cnt)
                                    ,'%20s' % vctstrade.getMarketName(df['market'][x])
                                    )

                            fund_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ( (float(df['trade_price'][x]) * buy_cnt) * 0.05 )   
                            print('### ___SELL_PLUS___',fund_amout)
                            buytarget = []
                            amount = []
                            buy_cnt = 0
                            buy_amount = 0
                            break

                        if  (((float(df['trade_price'][x]) - float(amount[0])) /  float(amount[0]) ) * 100) < -3.35:
                            print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                            print('%15s' % 'market'                
                                    ,'%7s' % 'change'
                                    ,'%12s' % '종가'
                                    ,'%12s' % '시가'
                                    ,'%13s' % '변화액'
                                    ,'%6s' % '변화율'
                                    ,'%12s' % 'buy_cnt'
                                    ,'%17s' % 'amount'
                                    ,'%23s' %  'market'
                                    )
                            print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                            for x in df.index:
                                print('%15s' % df['market'][x]
                                    ,'%6s' % df['change'][x]
                                    ,'%15f' % df['trade_price'][x]
                                    ,'%15f' % amount[0]
                                    ,'%15f' % (float(df['trade_price'][x]) - float(amount[0]))
                                    ,'%10f' % (((float(df['trade_price'][x]) - float(amount[0])) /  float(amount[0]) ) * 100)
                                    ,'%15f' % buy_cnt
                                    ,'%15f' % (float(df['trade_price'][x]) * buy_cnt)
                                    ,'%20s' % vctstrade.getMarketName(df['market'][x])
                                    )
                            fund_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ( (float(df['trade_price'][x]) * buy_cnt) * 0.05 )   
                            print('### ___SELL_MINUS___',fund_amout)
                            buytarget = []
                            amount = []
                            buy_cnt = 0
                            buy_amount = 0
                            break

                        time.sleep(1)
            else:
                print('stand by...')
            
            if(loop == True):
                time.sleep(looptime)
            else:
                break

       

#################################################
# main
if __name__ == '__main__':
    # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()

    # moinitor markets info
            # signed_change_rate 변화율
            # trade_volume	가장 최근 거래량	
            # acc_trade_price	누적 거래대금(UTC 0시 기준)	
            # acc_trade_price_24h	24시간 누적 거래대금	
            # acc_trade_volume	누적 거래량(UTC 0시 기준)	
            # acc_trade_volume_24h	24시간 누적 거래량	
    # monitorMarkets(loop=False,looptime=3,sort='signed_change_rate',change='RISE',market='KRW',trade_price=1000)
    # monitorMarkets(loop=True,looptime=5,sort='signed_change_rate',market='KRW')

    # watch jump market info 
    watchJumpMarkets(loop=True, looptime=60, period=10, market='KRW', trade_price = 1000)

    # scheduler = BlockingScheduler()
    # scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    # try:
    #    scheduler.start()
    # except Exception as err:
    #    logger.error(' main Exception : %s' % e)