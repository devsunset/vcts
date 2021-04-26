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
from common import common

##################################################
# constant

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

comm = common.Common()

# vcts_trade,VctsTrade
vctstrade  = vcts_trade.VctsTrade()

# buy choose up rate
BUY_CHOOSE_PLUS_RATE = 0.25

# condition rate value
SELL_PLUS_RATE = 1.25 
SELL_MINUS_RATE = -1.25
SELL_HOLD_EXIT_RATE = 0.55 #(commision - even value)

# upbit krw market commission
COMMISSION = 0.005

##################################################
# biz function

# market monitor
def monitorMarkets(loop=False, looptime=3, sort='signed_change_rate', targetMarket=['KRW','BTC','USDT']):
    selectMarkets = []

    ### TYPE ONE
    markets = vctstrade.getMarkets()
    for i in markets.index:
        if markets['market_type'][i] in targetMarket:
            selectMarkets.append(markets['market'][i])

    ### TYPE TWO
    # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    # columns = ['opening_price','trade_price']
    # selectMarkets = vctstrade.getChoiceGrowsMarkets(columns,3,3,3,3)

    ### TYPE THREE 
    # selectMarkets.append('KRW-DOGE')

    ###########################################################################################
    while True:
        # get ticker market data
        df = vctstrade.getTickerMarkets(selectMarkets).sort_values(by=sort, ascending=False)

        # merge market info & ticker market data
        df = pd.merge(df, markets, on = 'market')

        # ------------------------------------------------------------------------
        # unused filed delete
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
        # market info
        # del df['korean_name']
        del df['english_name']
        del df['market_warning']
        del df ['market_type']
        # ------------------------------------------------------------------------

        # column align
        columns = df.columns.tolist()
        colalignList = []
        for colname in columns:
            if 'change' == colname or 'market_type' == colname or  'market_warning' == colname or colname.find('_date') > -1 or colname.find('_time') > -1 or colname.find('_timestamp') > -1:
                colalignList.append("center")
            elif 'korean_name' == colname or 'english_name' == colname :        
                colalignList.append("left")
            else:
                colalignList.append("right")

        #  tabulate Below are all the styles that you can use :
        # “plain” “simple” “github” “grid” “fancy_grid” “pipe” “orgtbl” “jira” “presto” “pretty” “psql” “rst” “mediawiki” “moinmoin” “youtrack” “html” “latex” “latex_raw” “latex_booktabs”  “textile”
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False, colalign=colalignList))

        if(loop == True):
            time.sleep(looptime)
        else:
            break

# watch jump markets
def watchJumpMarkets(looptime=5, period=12, market=None, targetMarket=['KRW','BTC','USDT'], trade_price=10000):
        if looptime < 2:
            logger.warning('looptime value invalid (minum 2 over) ...')
            return 
        if period < 6:
            logger.warning('period value invalid (minum 6 over) ...')
            return 
        # makret + trade_price = 2
        period = period+2

        print('SELL_PLUS_RATE:',SELL_PLUS_RATE,', SELL_HOLD_EXIT_RATE:',SELL_HOLD_EXIT_RATE,', SELL_MINUS_RATE:',SELL_MINUS_RATE)

        selectMarkets = []
        buymarket = []
        history_df =  pd.DataFrame()
        fund_amount = 300000
        idx=0
        sell_up_count = 0
        sell_hold_exit_count = 0
        sell_down_count = 0

        # get market info data
        markets = vctstrade.getMarkets()
        for i in markets.index:
            if markets['market_type'][i] in targetMarket:
                selectMarkets.append(markets['market'][i])
        # selectMarkets = ['KRW-DOGE']

        while True:
            # buy market exist skip 
            if  len(buymarket) == 0:
                # market info data
                stand_df = pd.DataFrame(selectMarkets, columns=['market'])

                # makret ticker data
                df = vctstrade.getTickerMarkets(selectMarkets).sort_values(by='signed_change_rate', ascending=False)

                # get market and trade_price value from market ticker data
                now_df =  pd.DataFrame(df, columns=['market','trade_price'])

                # copy trade_price column  to time column
                now_df[datetime.datetime.now().strftime("%H:%M:%S")] = now_df['trade_price']

                # history_df merge now ticker data
                if len(history_df) == 0:
                    history_df = pd.merge(stand_df, now_df, on = 'market')
                else:
                    del history_df['trade_price']
                    history_df = pd.merge(history_df, now_df, on = 'market')

                # history_df column sort    (mkaret , trade_price , ......)
                temp_headers = history_df.columns.tolist()
                headers  = []
                headers.append('market')
                headers.append('trade_price')
                for x in temp_headers:
                    if x !='market' and x !='trade_price':
                        headers.append(x)
                history_df = history_df.reindex(columns=headers)

                # old period data delete - contain period count data
                if len (history_df.columns.tolist()) > period :                
                    del history_df[history_df.columns.tolist()[2]]

                # copy history_df to analysis_df
                analysis_df = history_df.copy()

                if len(history_df.columns.tolist()) == period:  
                    # add diff column             
                    for i in range(period-3):
                        analysis_df['diff_'+str(i+1)] = history_df[history_df.columns.tolist()[1]] - history_df[history_df.columns.tolist()[i+2]]
                    # add rate column
                    for i in range(period-3):
                        analysis_df['rate_'+str(i+1)] =  (analysis_df['diff_'+str(i+1)] / history_df[history_df.columns.tolist()[1]]) * 100
                    
                    # sort last rate value
                    tdf = analysis_df.sort_values(by='rate_'+str(period-3), ascending=False)

                    logger.warning('monitor market ... -> plus : '+str(sell_up_count)+' minus : '+str(sell_down_count)+' hold : '+str(sell_hold_exit_count)+' fund : '+str(fund_amount))

                    # choose buy market 
                    centerCol =  tdf.columns.tolist()[int((period-1)/2)]
                    lastCol =   tdf.columns.tolist()[period-1]

                    buymarketTemp = {}
                    for x in tdf.index:
                        #  trade_price over skip
                        if trade_price is not None:
                            if int(tdf['trade_price'][x]) > trade_price :
                                continue
                        ###########################################
                        #  KEY POINT LOGIC
                        ###########################################
                        centerval = float(tdf[centerCol][x])
                        lastval = float(tdf[lastCol][x])
                        period_rate = ((lastval - centerval) / centerval ) * 100

                        pre_rate_down_check = False
                        for s in range(1,int((period-1)/2)):
                            if float(tdf['rate_'+str(s)][x]) > 0 :
                                pre_rate_down_check = True
                                break
                        if pre_rate_down_check:
                            continue

                        if float(tdf['rate_'+str(period-3)][x]) >= BUY_CHOOSE_PLUS_RATE :
                            pass
                        else:
                            if period_rate < BUY_CHOOSE_PLUS_RATE:
                                    continue
                            else:
                                if float(tdf['rate_'+str(period-3)][x]) <= 0.1 :
                                    continue
                                       
                        # buymarketTemp add
                        buymarketTemp[tdf['market'][x]] = tdf['trade_price'][x]
                    # print(buymarketTemp)

                    if len(buymarketTemp) > 0 :
                      for key, value in buymarketTemp.items():    
                            # print(tabulate(vctstrade.getCandlesMinutes(unit=1,market=key,count=10), headers='keys', tablefmt='psql'))
                            bdf = vctstrade.getCandlesMinutes(unit=1,market=key,count=10)
                            plusValue = float(value) + ((float(value) * SELL_PLUS_RATE)/10)
                            minusValue = float(value) + ((float(value) * SELL_MINUS_RATE)/10)
                            # print(value,plusValue,minusValue)
                            plusCheck = 0
                            minusCheck = 0
                            for x in bdf.index:
                                if float(bdf['trade_price'][x]) >= plusValue :
                                    plusCheck = plusCheck +1
                                if float(bdf['trade_price'][x]) <= minusValue :
                                    minusCheck = minusCheck +1

                            if (plusCheck > 0 and minusCheck == 0 ):
                                buymarket.append(key)

                    ###########################################

                    # buy market logic 
                    if len(buymarket) > 0 :
                        ###########################################
                        dfx = vctstrade.getTickerMarkets(buymarket)
                        ###########################################

                        choice = []
                        for x in dfx.index:
                            choice.append(dfx['market'][x])
                            amount = dfx['trade_price'][x]
                            break

                        buy_cnt = fund_amount/float(amount)
                        fund_amount = fund_amount - (buy_cnt * float(amount))
                        hold_exit = 0

                        while True:
                            logger.warning('----------------------------------------------------------------------------------------------------------------------------------')
                            df = vctstrade.getTickerMarkets(choice)
                            buy_amount = buy_cnt * float(amount)

                            for x in df.index:
                                print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■'
                                    ,df['market'][x] +' : '+vctstrade.getMarketName(df['market'][x])
                                    ,'PRICE:'
                                    ,'%12f' % amount
                                    ,'%12f' % df['trade_price'][x]
                                    ,'DIFF:'
                                    ,'%12f' % (float(df['trade_price'][x]) - float(amount))
                                    ,'RATE:'
                                    ,'% 4f' % (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100)
                                    ,'FUND:'
                                    ,'%12f' % ((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ))
                                    )

                            if (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) >= SELL_PLUS_RATE:
                                    sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                                    print('#######################################################')
                                    print('### [SELL_PLUS] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                                    print('#######################################################')
                                    # comm.log('[PLUS] '+vctstrade.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ))),'Y')
                                    fund_amount = fund_amount + sell_amout
                                    buymarket = []
                                    buy_cnt = 0
                                    buy_amount = 0
                                    sell_up_count = sell_up_count+1
                                    history_df =  pd.DataFrame()
                                    break

                            if hold_exit > ((30*2) * 5):
                                if  (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) >= SELL_HOLD_EXIT_RATE:
                                    sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                                    print('#######################################################')
                                    print('### [SELL_HOLD_EXIT] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                                    print('#######################################################')
                                    # comm.log('[HOLD_EXIT] '+vctstrade.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ))),'Y')
                                    fund_amount = fund_amount + sell_amout
                                    buymarket = []
                                    buy_cnt = 0
                                    buy_amount = 0
                                    sell_hold_exit_count = sell_hold_exit_count+1
                                    history_df =  pd.DataFrame()
                                    break

                            if (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) <= SELL_MINUS_RATE:
                                bdf = vctstrade.getCandlesMinutes(unit=1,market=key,count=30)
                                minusValue = float(df['trade_price'][x])
                                plusCheck = 0
                                minusCheck = 0
                                for x in bdf.index:
                                    if float(bdf['trade_price'][x]) <= minusValue :
                                        minusCheck = minusCheck +1
                                if (minusCheck == 0 ):                                    
                                    sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION )   
                                    print('#######################################################')
                                    print('### [SELL_MINUS] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ) ,' = ', sell_amout)
                                    print('#######################################################')
                                    # comm.log('[MINUS] '+vctstrade.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * COMMISSION ))),'Y')
                                    fund_amount = fund_amount + sell_amout
                                    buymarket = []
                                    buy_cnt = 0
                                    buy_amount = 0
                                    sell_down_count = sell_down_count+1
                                    history_df =  pd.DataFrame()
                                    break

                            hold_exit = hold_exit+1

                            time.sleep(2)
                else:
                    logger.warning('ready ...')

            time.sleep(looptime)

#################################################
# main
if __name__ == '__main__':
    # watch jump market info 
    watchJumpMarkets(looptime=5, period=6, targetMarket=['KRW'])

    # moinitor markets info
    # monitorMarkets(loop=False, looptime=5, sort='signed_change_rate', targetMarket=['KRW'])

    ###############################################

    # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()

    # scheduler = BlockingScheduler()
    # scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    # try:
    #    scheduler.start()
    # except Exception as err:
    #    logger.error(' main Exception : %s' % e)