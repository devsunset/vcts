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
from tabulate import tabulate
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

# upbit commission
COMMISSION = 0.005

# sell up rate
SELL_UP_RATE = 1.5
SELL_UP_MAX_RATE = 3.0
SELL_UP_SKIP_RATE = 1.55
SELL_HOLD_UP_RATE = 0.55

# sell down rate
SELL_DOWN_RATE = -1.45

##################################################
# biz function

# market monitor
def monitorMarkets(loop=False, looptime=3, sort='signed_change_rate', change=None):
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
        # get ticker market data
        df = vctstrade.getTickerMarkets(best).sort_values(by=sort, ascending=False)

        # merge market info & ticker market data
        df = pd.merge(df, markets, on = 'market')

        # unused filed delete
        # market info
        del df['id']
        del df['korean_name']
        del df['english_name']
        del df['market_warning']
        # ticker market data
        # del df['market'] #종목 구분 코드	
        del df['trade_date'] 	#최근 거래 일자(UTC)	
        del df['trade_time'] 	#최근 거래 시각(UTC)	
        del df['trade_date_kst'] 	#최근 거래 일자(KST)	
        del df['trade_time_kst'] 	#최근 거래 시각(KST)	
        del df['trade_timestamp'] 	#최근 거래  타임스탬프	
        # del df['opening_price'] 	#시가	
        # del df['high_price'] 	#고가	
        # del df['low_price'] 	#저가	
        # del df['trade_price'] 	#종가	
        # del df['prev_closing_price'] 	#전일 종가	
        # del df['change'] 	#EVEN : 보합 RISE : 상승 FALL : 하락	
        del df['change_price'] 	#변화액의 절대값	
        del df['change_rate'] 	#변화율의 절대값	
        # del df['signed_change_price'] 	#부호가 있는 변화액	
        # del df['signed_change_rate'] 	#부호가 있는 변화율	
        # del df['trade_volume'] 	#가장 최근 거래량	
        del df['acc_trade_price'] 	#누적 거래대금(UTC 0시 기준)	
        # del df['acc_trade_price_24h'] 	#24시간 누적 거래대금	
        del df['acc_trade_volume'] 	#누적 거래량(UTC 0시 기준)	
        # del df['acc_trade_volume_24h'] 	#24시간 누적 거래량	
        del df['highest_52_week_price'] 	#52주 신고가	
        del df['highest_52_week_date'] 	#52주 신고가 달성일	
        del df['lowest_52_week_price'] 	#52주 신저가	
        del df['lowest_52_week_date'] 	#52주 신저가 달성일	
        del df['timestamp'] 	#타임스탬프	

        #  tabulate Below are all the styles that you can use :
        # “plain” “simple” “github” “grid” “fancy_grid” “pipe” “orgtbl” “jira” “presto” “pretty” “psql” “rst” “mediawiki” “moinmoin” “youtrack” “html” “latex” “latex_raw” “latex_booktabs”  “textile”

        # displaying the DataFrame
        print(tabulate(df, headers = 'keys', tablefmt = 'psql'))

        if(loop == True):
            time.sleep(looptime)
        else:
            break

# watch jump markets
def watchJumpMarkets(looptime=10, period=7, market=None, trade_price=None):
        if period < 5:
            logger.warning('period value invalid (minum 5 over) ...')
            return 

        idx=0
        history_df =  pd.DataFrame()
        best = []
        # best.append('KRW-DOGE')
        fund_amount = 300000
        SELL_UP_COUNT = 0
        SELL_HOLD_EXIT_COUNT = 0
        SELL_DOWN_COUNT = 0

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

                logger.warning('monitor market ... -> SELL_UP_COUNT : '+str(SELL_UP_COUNT)+' SELL_DOWN_COUNT : '+str(SELL_DOWN_COUNT)+' SELL_HOLD_EXIT_COUNT : '+str(SELL_HOLD_EXIT_COUNT))

                buytarget = []

                for x in tdf.index:

                    if market is not None:
                        tmp = tdf['market'][x]
                        if tmp[:tmp.find('-')] not in market.split('|'):
                            continue

                    if trade_price is not None:
                        if int(tdf['trade_price'][x]) > 1000 :
                            continue
                    
                    for c in range(1, (period-2)):
                        if float(tdf['rate_'+str(c)][x]) > 0 :
                                continue

                    if float(tdf['rate_'+str(period-3)][x]) < 0.15 :
                            continue

                    buytarget.append(tdf['market'][x])

                if len(buytarget) > 0 :
                     # signed_change_rate 변화율
                     # trade_volume	가장 최근 거래량	
                     dfx = vctstrade.getTickerMarkets(buytarget).sort_values(by='trade_volume', ascending=False)

                     choice = []
                     for x in dfx.index:
                        choice.append(dfx['market'][x])
                        amount = dfx['trade_price'][x]
                        break

                     buy_cnt = fund_amount/float(amount)
                     fund_amount = fund_amount - (buy_cnt * float(amount))
                     up_skip = 0
                     hold_exit = 0

                     while True:
                        logger.warning('check ------------------  ')
                        df = vctstrade.getTickerMarkets(choice).sort_values(by='signed_change_rate', ascending=False)
                        buy_amount = buy_cnt * float(amount)
                        
                        # print('-----------------------------------------------------------------------------------------------------------------------------------------------')
                        # print('%15s' % 'market'                
                        #         ,'%7s' % 'change'
                        #         ,'%12s' % '구매가'
                        #         ,'%12s' % '현재가'
                        #         ,'%12s' % '변화액'
                        #         ,'%6s' % '변화율'
                        #         ,'%12s' % '구매수량'
                        #         ,'%10s' % '자산현황'
                        #         ,'%22s' %  'name'
                        #         )
                        # print('-----------------------------------------------------------------------------------------------------------------------------------------------')
                        # for x in df.index:
                        #     print('%15s' % df['market'][x]
                        #         ,'%6s' % df['change'][x]
                        #         ,'%15f' % amount
                        #         ,'%15f' % df['trade_price'][x]
                        #         ,'%15f' % (float(df['trade_price'][x]) - float(amount))
                        #         ,'%10f' % (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100)
                        #         ,'%15f' % buy_cnt
                        #         ,'%15f' % ((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ))
                        #         ,'%20s' % vctstrade.getMarketName(df['market'][x])
                        #         )

                        for x in df.index:
                            print('%15s' % df['market'][x]
                                ,'%6s' % df['change'][x]
                                ,'%15f' % amount
                                ,'%15f' % df['trade_price'][x]
                                ,'%15f' % (float(df['trade_price'][x]) - float(amount))
                                ,'%10f' % (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100)
                                ,'%15f' % buy_cnt
                                ,'%15f' % ((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ))
                                ,'%20s' % vctstrade.getMarketName(df['market'][x])
                                )

                        if up_skip > 0:
                            if  up_skip >= (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) and (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) > SELL_UP_RATE:
                                hold_exit = 0
                                if  (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) > SELL_UP_MAX_RATE:
                                    sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                                    print('#######################################')
                                    print('### ___SELL_PLUS___###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                                    print('#######################################')
                                    fund_amount = fund_amount + sell_amout
                                    buytarget = []
                                    buy_cnt = 0
                                    buy_amount = 0
                                    SELL_UP_COUNT = SELL_UP_COUNT+1
                                    break
                            elif (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) > SELL_UP_SKIP_RATE:
                                hold_exit = 0
                            else:
                                sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                                print('#######################################')
                                print('### ___SELL_PLUS___###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                                print('#######################################')
                                fund_amount = fund_amount + sell_amout
                                buytarget = []
                                buy_cnt = 0
                                buy_amount = 0
                                SELL_UP_COUNT = SELL_UP_COUNT+1
                                break

                        if  (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) > SELL_UP_RATE:
                            up_skip = (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )  

                        if  (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) < SELL_DOWN_RATE:
                            sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                            print('#######################################')
                            print('### ___SELL_MINUS___###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                            print('#######################################')
                            fund_amount = fund_amount + sell_amout
                            buytarget = []
                            buy_cnt = 0
                            buy_amount = 0
                            SELL_DOWN_COUNT = SELL_DOWN_COUNT+1
                            break

                        if hold_exit > 300:
                            if  (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) > SELL_HOLD_UP_RATE:
                                sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                                print('#######################################')
                                print('### ___SELL_HOLD_EXIST___###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                                print('#######################################')
                                fund_amount = fund_amount + sell_amout
                                buytarget = []
                                buy_cnt = 0
                                buy_amount = 0
                                SELL_HOLD_EXIT_COUNT = SELL_HOLD_EXIT_COUNT+1
                                break

                        hold_exit = hold_exit+1
                        time.sleep(3)
            else:
                logger.warning('ready ...')

            time.sleep(looptime)

#################################################
# main
if __name__ == '__main__':
    # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()

    # moinitor markets info
    monitorMarkets(loop=False,looptime=5,sort='signed_change_rate')

    # watch jump market info 
    # watchJumpMarkets(looptime=5, period=7)

    # scheduler = BlockingScheduler()
    # scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    # try:
    #    scheduler.start()
    # except Exception as err:
    #    logger.error(' main Exception : %s' % e)