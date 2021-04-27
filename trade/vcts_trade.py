# -*- coding: utf-8 -*-
##################################################
#
#         trade.py
#
##################################################

##################################################
# import

import datetime
from pandas import DataFrame
from tabulate import tabulate
import pandas as pd
import numpy as np
import logging
import logging.config
from os import path
import time
import json
import sqlite3
import sys

from common import config
from common import common
from upbitapi import upbitapi

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

# logging config
log_file_path = path.join(path.abspath(path.dirname(path.abspath(path.dirname(__file__)))), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

comm = common.Common()
upbitapi = upbitapi.UpbitApi(config.ACCESS_KEY, config.SECRET)

MARKETS  = {}

# init investment
INIT_INVESTMENT = 300000

# upbit krw market commission
UPBIT_KRW_COMMISSION = 0.005

# buy check time sleep
BUY_CHECK_TIME_SLEEP = 2

# condition rate value
TARGET_BUY_RATE_1 = 0.25
SELL_PLUS_RATE_1 = 1.0
SELL_MINUS_RATE_1 = -1.5

TARGET_BUY_RATE_2 = 5.0
SELL_PLUS_RATE_2 = 5.5
SELL_MINUS_RATE_2 = -3.5

TARGET_BUY_RATE_3 = 5.0
SELL_PLUS_RATE_3 = 5.5
SELL_MINUS_RATE_3 = -3.5

##################################################
# biz function

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 250)

class VctsTrade():
    def __init__(self):
        self.loadMarketSaveToDb()

    # load market info save to db (vcts_meta table).
    def loadMarketSaveToDb(self):
        logger.warn('loadMarketSaveToDb start')
        data_json = upbitapi.getQuotationMarketAll()
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vcts_meta'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name text, market_warning text)'
            comm.executeTxDB(conn, sqlText)

            logger.warn('loadMarketSaveToDb db_init')

            sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning)'
            sqlText += ' values (?, ?, ?, ?)'

            sqlParam = []
            for data in data_json:       
                data.setdefault('market_warning', '')         
                sqlParam.append((data.get('market'),data.get('korean_name'),data.get('english_name'),data.get('market_warning')))
                MARKETS[data['market']] =  data['korean_name']

            comm.executeTxDB(conn, sqlText, sqlParam)
            conn.commit()
            logger.warn('loadMarketSaveToDb db_save')
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()

    # get market name  info
    def getMarketName(self,market):        
        return MARKETS[market]

    # get markets info
    def getMarkets(self):        
        markets = comm.searchDB("select market,korean_name,english_name,market_warning,substr(market,0,instr(market,'-')) as market_type from vcts_meta")
        return markets

    # get ticker markets
    def getTickerMarkets(self,markets):
        return pd.DataFrame(upbitapi.getQuotationTicker(markets))

    # get candles minutes
    def getCandlesMinutes(self, unit, market, count):
        return pd.DataFrame(upbitapi.getQuotationCandlesMinutes(unit=unit, market=market, count=count))

    ##########################################################

    #  get markets candles mwd data save to db
    def loadMarketsCandlesMwdData(self):
        self.loadMarketCandlesMonthsSaveToDb()
        self.loadMarketCandlesWeeksSaveToDb()
        self.loadMarketCandlesDaysSaveToDb()

    # load market candles day info save to db (vcts_candles_day table).
    def loadMarketCandlesDaysSaveToDb(self):
        logger.warn('loadMarketCandlesDaysSaveToDb start')
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vcts_candles_days'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vcts_candles_days (market text, candle_date_time_utc text, candle_date_time_kst text, opening_price real, high_price real, low_price real, trade_price real, timestamp integer, candle_acc_trade_price real, candle_acc_trade_volume real, prev_closing_price real, change_price real,  change_rate real, converted_trade_price real)'
            comm.executeTxDB(conn, sqlText)

            logger.warn('loadMarketCandlesDaysSaveToDb db_init')

            markets = self.getMarkets()
   
            sqlText = 'insert into vcts_candles_days  (market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price, timestamp, candle_acc_trade_price, candle_acc_trade_volume, prev_closing_price, change_price,  change_rate, converted_trade_price)'
            sqlText += ' values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,  ?, ?)'

            for i in markets.index:
                logger.warn(markets['market'][i]+" : "+markets['korean_name'][i])
                data_json = upbitapi.getQuotationCandlesDays(market=markets['market'][i],count=config.CANDLES_DAY_COUNT,convertingPriceUnit=config.CONVERTING_PRICE_UNIT)

                sqlParam = []
                for data in data_json:                
                    sqlParam.append((data.get('market'),data.get('candle_date_time_utc'),data.get('candle_date_time_kst'),data.get('opening_price'),data.get('high_price'),data.get('low_price'),data.get('trade_price'),data.get('timestamp'),data.get('candle_acc_trade_price'),data.get('candle_acc_trade_volume'),data.get('prev_closing_price'),data.get('change_price'),data.get('change_rate'),data.get('converted_trade_price')))

                comm.executeTxDB(conn, sqlText, sqlParam)

            conn.commit()
            logger.warn('loadMarketCandlesDaysSaveToDb db_save')
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()        

    # load market candles weeks info save to db (vcts_candles_week table).
    def loadMarketCandlesWeeksSaveToDb(self):
        logger.warn('loadMarketCandlesWeeksSaveToDb start')
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vcts_candles_weeks'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vcts_candles_weeks (market text, candle_date_time_utc text, candle_date_time_kst text, opening_price real, high_price real, low_price real, trade_price real, timestamp integer, candle_acc_trade_price real, candle_acc_trade_volume real, first_day_of_period  text)'
            comm.executeTxDB(conn, sqlText)

            logger.warn('loadMarketCandlesWeeksSaveToDb db_init')

            markets = self.getMarkets()
   
            sqlText = 'insert into vcts_candles_weeks  (market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price, timestamp, candle_acc_trade_price, candle_acc_trade_volume, first_day_of_period)'
            sqlText += ' values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

            for i in markets.index:
                logger.warn(markets['market'][i]+" : "+markets['korean_name'][i])
                data_json = upbitapi.getQuotationCandlesWeeks(market=markets['market'][i],count=config.CANDLES_WEEK_COUNT)

                sqlParam = []
                for data in data_json:                
                    sqlParam.append((data.get('market'),data.get('candle_date_time_utc'),data.get('candle_date_time_kst'),data.get('opening_price'),data.get('high_price'),data.get('low_price'),data.get('trade_price'),data.get('timestamp'),data.get('candle_acc_trade_price'),data.get('candle_acc_trade_volume'),data.get('first_day_of_period')))

                comm.executeTxDB(conn, sqlText, sqlParam)

            conn.commit()
            logger.warn('loadMarketCandlesWeeksSaveToDb db_save')
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()

    # load market candles months info save to db (vcts_candles_week table).
    def loadMarketCandlesMonthsSaveToDb(self):
        logger.warn('loadMarketCandlesMonthsSaveToDb start')
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vcts_candles_months'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vcts_candles_months (market text, candle_date_time_utc text, candle_date_time_kst text, opening_price real, high_price real, low_price real, trade_price real, timestamp integer, candle_acc_trade_price real, candle_acc_trade_volume real, first_day_of_period  text)'
            comm.executeTxDB(conn, sqlText)

            logger.warn('loadMarketCandlesMonthsSaveToDb db_init')

            markets = self.getMarkets()
   
            sqlText = 'insert into vcts_candles_months  (market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price, timestamp, candle_acc_trade_price, candle_acc_trade_volume, first_day_of_period)'
            sqlText += ' values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

            for i in markets.index:
                logger.warn(markets['market'][i]+" : "+markets['korean_name'][i])
                data_json = upbitapi.getQuotationCandlesMonths(market=markets['market'][i],count=config.CANDLES_MONTH_COUNT)

                sqlParam = []
                for data in data_json:                
                    sqlParam.append((data.get('market'),data.get('candle_date_time_utc'),data.get('candle_date_time_kst'),data.get('opening_price'),data.get('high_price'),data.get('low_price'),data.get('trade_price'),data.get('timestamp'),data.get('candle_acc_trade_price'),data.get('candle_acc_trade_volume'),data.get('first_day_of_period')))

                comm.executeTxDB(conn, sqlText, sqlParam)

            conn.commit()
            logger.warn('loadMarketCandlesMonthsSaveToDb db_save')
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()     

    # query continue growth markets
    def queryContinueGrowsMarkets(self, date_type="M", whereCondition=None, recent_count = "33"):
        sqlText = '''
                            SELECT  
                            a.market, a.korean_name , a.english_name, a.market_warning
                            #__SEARCH_QUERY__#
                            FROM
                            vcts_meta a
                            #__JOIN_QUERY__#
                            WHERE  1=1
                            #__WHERE_QUERY__#
                        '''
        search_query =""
        join_query =""
        where_query = ""
        
        target_table = ""
        if date_type == "M":
            target_table = " vcts_candles_months "
        elif date_type == "W":
            target_table = " vcts_candles_weeks "
        else:
            target_table = " vcts_candles_days "

        columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
        date_query = "select candle_date_time_utc from( select distinct candle_date_time_utc from  "+target_table+" order by candle_date_time_utc desc limit "+recent_count +" ) order by candle_date_time_utc asc"
        date_info = comm.searchDB(date_query)

        for i in date_info.index:
            for c in columns:
                search_query +=", x"+str(i)+"."+c+" "
            join_query += " LEFT OUTER JOIN (select * from "+target_table+" where candle_date_time_utc = '"+date_info['candle_date_time_utc'][i]+"') x"+str(i)+" ON x"+str(i)+".market = a.market "

        sqlText = sqlText.replace("#__SEARCH_QUERY__#",search_query)
        sqlText = sqlText.replace("#__JOIN_QUERY__#",join_query)

        if whereCondition is not None:
            dates = list(range(0, len(date_info.index)))
            for w in whereCondition:
                where_query += " AND ( "
                for  idx in dates:                    
                    if idx < len(dates)-1:
                        where_query += "x"+str((idx+1))+"."+w+" >  x"+str(idx)+"."+w
                        if idx < len(dates)-2:
                            where_query += " and "
                where_query += " )"

        sqlText = sqlText.replace("#__WHERE_QUERY__#",where_query)

        coins = comm.searchDB(sqlText)

        return coins

    # get choice growths markets
    def getChoiceGrowsMarkets(self,columns,m=2,w=2,d=2,count=1):
        coinsMonth = self.queryContinueGrowsMarkets("M",columns,str(m))
        coinsWeek = self.queryContinueGrowsMarkets("W",columns,str(w))
        coinsDay = self.queryContinueGrowsMarkets("D",columns,str(d))

        coins = {}

        for i in coinsMonth.index:
            coins[coinsMonth['market'][i]] = 1
        for i in coinsWeek.index:
            key = coinsWeek['market'][i]
            if key not in coins:
                coins[coinsWeek['market'][i]] = 1
            else:
                coins[coinsWeek['market'][i]] = 1 + int(coins[coinsWeek['market'][i]])
        for i in coinsDay.index:
            key = coinsDay['market'][i]
            if key not in coins:
                coins[coinsDay['market'][i]] = 1
            else:
                coins[coinsDay['market'][i]] = 1 + int(coins[coinsDay['market'][i]])

        best = []

        if len(coins) > 0 :
            for c in coins.keys():
                if coins[c] >= count:
                    best.append(c)

        return best

    ##########################################################

    # market monitor
    def monitorMarkets(self, loop=False, looptime=3, sort='signed_change_rate', targetMarket=['KRW','BTC','USDT']):
        selectMarkets = []

        ### TYPE ONE
        markets = self.getMarkets()
        for i in markets.index:
            if markets['market_type'][i] in targetMarket:
                selectMarkets.append(markets['market'][i])

        ### TYPE TWO
        # get continue grows coins
        # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
        # columns = ['opening_price','trade_price']
        # selectMarkets = self.getChoiceGrowsMarkets(columns,3,3,3,3)

        ### TYPE THREE 
        # selectMarkets.append('KRW-DOGE')

        ###########################################################################################
        while True:
            # get ticker market data
            df = self.getTickerMarkets(selectMarkets).sort_values(by=sort, ascending=False)

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

    # automatic trade1
    def automaticTrade_1(self, looptime=2, period=6, market=None, targetMarket=['KRW','BTC','USDT'], max_trade_price=10000):
            if looptime < 2:
                logger.warning('looptime value invalid (minum 2 over) ...')
                return 
            if period < 6:
                logger.warning('period value invalid (minum 6 over) ...')
                return 
            # makret + trade_price = 2
            period = period+2

            print('SELL_PLUS_RATE_1:',SELL_PLUS_RATE_1,', SELL_MINUS_RATE_1:',SELL_MINUS_RATE_1)

            selectMarkets = []
            buymarket = []
            history_df =  pd.DataFrame()
            investment_amount = INIT_INVESTMENT
            idx=0
            sell_plus_count = 0
            sell_minus_count = 0

            # get market info data
            markets = self.getMarkets()
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
                    df = self.getTickerMarkets(selectMarkets).sort_values(by='signed_change_rate', ascending=False)

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

                        logger.warning('monitor market ... -> plus : '+str(sell_plus_count)+' minus : '+str(sell_minus_count)+' investment : '+str(investment_amount))

                        # choose buy market 
                        centerCol =  tdf.columns.tolist()[int((period-1)/2)]
                        lastCol =   tdf.columns.tolist()[period-1]

                        buymarketTemp = {}
                        for x in tdf.index:
                            #  max_trade_price over skip
                            if max_trade_price is not None:
                                if int(tdf['trade_price'][x]) > max_trade_price :
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

                            if float(tdf['rate_'+str(period-3)][x]) >= TARGET_BUY_RATE_1 :
                                pass
                            else:
                                if period_rate < TARGET_BUY_RATE_1:
                                        continue
                                else:
                                    if float(tdf['rate_'+str(period-3)][x]) <= 0.1 :
                                        continue
                                        
                            # buymarketTemp add
                            buymarketTemp[tdf['market'][x]] = tdf['trade_price'][x]
                        # print(buymarketTemp)

                        if len(buymarketTemp) > 0 :
                            for key, value in buymarketTemp.items():    
                                    # print(tabulate(self.getCandlesMinutes(unit=1,market=key,count=15), headers='keys', tablefmt='psql'))
                                    bdf = self.getCandlesMinutes(unit=1,market=key,count=15)
                                    plusValue = float(value) + ((float(value) * SELL_PLUS_RATE_1)/10)
                                    minusValue = float(value) + ((float(value) * SELL_MINUS_RATE_1)/10)
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
                            dfx = self.getTickerMarkets(buymarket)
                            choice = []
                            for x in dfx.index:
                                choice.append(dfx['market'][x])
                                amount = dfx['trade_price'][x]
                                break

                            buy_cnt = investment_amount/float(amount)
                            investment_amount = investment_amount - (buy_cnt * float(amount))

                            while True:
                                logger.warning('----------------------------------------------------------------------------------------------------------------------------------')
                                df = self.getTickerMarkets(choice)
                                buy_amount = buy_cnt * float(amount)

                                for x in df.index:
                                    print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■'
                                        ,df['market'][x] +' : '+self.getMarketName(df['market'][x])
                                        ,', PRICE:'
                                        ,'%12f' % amount
                                        ,'%12f' % df['trade_price'][x]
                                        ,', DIFF:'
                                        ,'%12f' % (float(df['trade_price'][x]) - float(amount))
                                        ,', RATE:'
                                        ,'% 4f' % (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100)
                                        ,', INVESTMENT:'
                                        ,'%12f' % ((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))
                                        )

                                if (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) >= SELL_PLUS_RATE_1:
                                        sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION )   
                                        print('#######################################################')
                                        print('### [SELL_PLUS] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ) ,' = ', sell_amout)
                                        print('#######################################################')
                                        # comm.log('[PLUS] '+self.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))),'Y')
                                        investment_amount = investment_amount + sell_amout
                                        buymarket = []
                                        buy_cnt = 0
                                        buy_amount = 0
                                        sell_plus_count = sell_plus_count+1
                                        history_df =  pd.DataFrame()
                                        break

                                if (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) <= SELL_MINUS_RATE_1:
                                    bdf = self.getCandlesMinutes(unit=1,market=key,count=30)
                                    minusValue = float(df['trade_price'][x])
                                    minusCheck = 0
                                    for x in bdf.index:
                                        if float(bdf['trade_price'][x]) <= minusValue :
                                            minusCheck = minusCheck +1
                                    if (minusCheck == 0 ):                                    
                                        sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION )   
                                        print('#######################################################')
                                        print('### [SELL_MINUS] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ) ,' = ', sell_amout)
                                        print('#######################################################')
                                        # comm.log('[MINUS] '+self.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))),'Y')
                                        investment_amount = investment_amount + sell_amout
                                        buymarket = []
                                        buy_cnt = 0
                                        buy_amount = 0
                                        sell_minus_count = sell_minus_count+1
                                        history_df =  pd.DataFrame()
                                        break

                                time.sleep(BUY_CHECK_TIME_SLEEP)
                    else:
                        logger.warning('ready ...')

                time.sleep(looptime)

    # automatic trade 2
    def automaticTrade_2(self, looptime=5, period=12, market=None, targetMarket=['KRW','BTC','USDT'], max_trade_price=10000):
            if looptime < 5:
                logger.warning('looptime value invalid (minum 5 over) ...')
                return 
            if period < 12:
                logger.warning('period value invalid (minum 12 over) ...')
                return 
            # makret + trade_price = 2
            period = period+2

            print('SELL_PLUS_RATE_2:',SELL_PLUS_RATE_2,', SELL_MINUS_RATE_2:',SELL_MINUS_RATE_2)

            selectMarkets = []
            buymarket = []
            history_df =  pd.DataFrame()
            investment_amount = INIT_INVESTMENT
            idx=0
            sell_plus_count = 0
            sell_minus_count = 0

            # get market info data
            markets = self.getMarkets()
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
                    df = self.getTickerMarkets(selectMarkets).sort_values(by='signed_change_rate', ascending=False)

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

                        logger.warning('monitor market ... -> plus : '+str(sell_plus_count)+' minus : '+str(sell_minus_count)+' investment : '+str(investment_amount))

                        buymarketTemp = {}
                        for x in tdf.index:
                            #  max_trade_price over skip
                            if max_trade_price is not None:
                                if int(tdf['trade_price'][x]) > max_trade_price :
                                    continue
                            ###########################################
                            #  KEY POINT LOGIC
                            ###########################################
                            pre_rate_down_check = False
                            for s in range(1,int((period-3))):
                                if float(tdf['rate_'+str(s)][x]) < 0 :
                                    pre_rate_down_check = True
                                    break
                            if pre_rate_down_check:
                                continue
                            
                            if float(tdf['rate_1'][x]) >= TARGET_BUY_RATE_2 :
                                pass
                            else:
                                continue
                                        
                            # buymarketTemp add
                            buymarketTemp[tdf['market'][x]] = tdf['trade_price'][x]
                        # print(buymarketTemp)

                        if len(buymarketTemp) > 0 :
                            for key, value in buymarketTemp.items():    
                                    # print(tabulate(self.getCandlesMinutes(unit=60,market=key,count=12), headers='keys', tablefmt='psql'))
                                    bdf = self.getCandlesMinutes(unit= 60,market=key,count=12)
                                    nowValue = float(value)
                                    # print(value,plusValue,minusValue)
                                    plusCheck = 0
                                    minusCheck = 0
                                    for x in bdf.index:
                                        if float(bdf['trade_price'][x]) >= nowValue :
                                            plusCheck = plusCheck +1

                                    if (plusCheck == 0 ):
                                        buymarket.append(key)

                            ###########################################

                        # buy market logic 
                        if len(buymarket) > 0 :
                            dfx = self.getTickerMarkets(buymarket)
                            choice = []
                            for x in dfx.index:
                                choice.append(dfx['market'][x])
                                amount = dfx['trade_price'][x]
                                break

                            buy_cnt = investment_amount/float(amount)
                            investment_amount = investment_amount - (buy_cnt * float(amount))

                            while True:
                                logger.warning('----------------------------------------------------------------------------------------------------------------------------------')
                                df = self.getTickerMarkets(choice)
                                buy_amount = buy_cnt * float(amount)
                                
                                for x in df.index:
                                    print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■'
                                        ,df['market'][x] +' : '+self.getMarketName(df['market'][x])
                                        ,', PRICE:'
                                        ,'%12f' % amount
                                        ,'%12f' % df['trade_price'][x]
                                        ,', DIFF:'
                                        ,'%12f' % (float(df['trade_price'][x]) - float(amount))
                                        ,', RATE:'
                                        ,'% 4f' % (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100)
                                        ,', INVESTMENT:'
                                        ,'%12f' % ((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))
                                        )

                                if (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) >= SELL_PLUS_RATE_2:
                                        sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION )   
                                        print('#######################################################')
                                        print('### [SELL_PLUS] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ) ,' = ', sell_amout)
                                        print('#######################################################')
                                        # comm.log('[PLUS] '+self.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))),'Y')
                                        investment_amount = investment_amount + sell_amout
                                        buymarket = []
                                        buy_cnt = 0
                                        buy_amount = 0
                                        sell_plus_count = sell_plus_count+1
                                        history_df =  pd.DataFrame()
                                        break

                                if (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100) <= SELL_MINUS_RATE_2:
                                        sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION )   
                                        print('#######################################################')
                                        print('### [SELL_MINUS] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ) ,' = ', sell_amout)
                                        print('#######################################################')
                                        # comm.log('[MINUS] '+self.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))),'Y')
                                        investment_amount = investment_amount + sell_amout
                                        buymarket = []
                                        buy_cnt = 0
                                        buy_amount = 0
                                        sell_minus_count = sell_minus_count+1
                                        history_df =  pd.DataFrame()
                                        break

                                time.sleep(BUY_CHECK_TIME_SLEEP)
                    else:
                        logger.warning('ready ...')

                time.sleep(looptime)

    # automatic trade 3
    def automaticTrade_3(self, looptime=5, period=12, market=None, targetMarket=['KRW','BTC','USDT'], max_trade_price=10000):
            if looptime < 5:
                logger.warning('looptime value invalid (minum 5 over) ...')
                return 
            if period < 12:
                logger.warning('period value invalid (minum 12 over) ...')
                return 
            # makret + trade_price = 2
            period = period+2

            print('SELL_PLUS_RATE_3:',SELL_PLUS_RATE_3,', SELL_MINUS_RATE_3:',SELL_MINUS_RATE_3)

            selectMarkets = []
            buymarket = []
            history_df =  pd.DataFrame()
            investment_amount = INIT_INVESTMENT
            idx=0
            sell_plus_count = 0
            sell_minus_count = 0

            # get market info data
            markets = self.getMarkets()
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
                    df = self.getTickerMarkets(selectMarkets).sort_values(by='signed_change_rate', ascending=False)

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

                        logger.warning('monitor market ... -> plus : '+str(sell_plus_count)+' minus : '+str(sell_minus_count)+' investment : '+str(investment_amount))

                        buymarketTemp = {}
                        for x in tdf.index:
                            #  max_trade_price over skip
                            if max_trade_price is not None:
                                if int(tdf['trade_price'][x]) > max_trade_price :
                                    continue
                            ###########################################
                            #  KEY POINT LOGIC
                            ###########################################
                            pre_rate_down_check = False
                            for s in range(1,int((period-3))):
                                if float(tdf['rate_'+str(s)][x]) < 0 :
                                    pre_rate_down_check = True
                                    break
                            if pre_rate_down_check:
                                continue
                            
                            if float(tdf['rate_1'][x]) >= TARGET_BUY_RATE_3 :
                                pass
                            else:
                                continue
                                        
                            # buymarketTemp add
                            buymarketTemp[tdf['market'][x]] = tdf['trade_price'][x]
                        # print(buymarketTemp)

                        if len(buymarketTemp) > 0 :
                            for key, value in buymarketTemp.items():    
                                    # print(tabulate(self.getCandlesMinutes(unit=60,market=key,count=12), headers='keys', tablefmt='psql'))
                                    bdf = self.getCandlesMinutes(unit= 60,market=key,count=12)
                                    nowValue = float(value)
                                    # print(value,plusValue,minusValue)
                                    plusCheck = 0
                                    minusCheck = 0
                                    for x in bdf.index:
                                        if float(bdf['trade_price'][x]) >= nowValue :
                                            plusCheck = plusCheck +1

                                    if (plusCheck == 0 ):
                                        buymarket.append(key)

                            ###########################################

                        # buy market logic 
                        if len(buymarket) > 0 :
                            dfx = self.getTickerMarkets(buymarket)
                            choice = []
                            for x in dfx.index:
                                choice.append(dfx['market'][x])
                                amount = dfx['trade_price'][x]
                                break

                            buy_cnt = investment_amount/float(amount)
                            investment_amount = investment_amount - (buy_cnt * float(amount))
                            check_amount = amount

                            while True:
                                logger.warning('----------------------------------------------------------------------------------------------------------------------------------')
                                df = self.getTickerMarkets(choice)
                                buy_amount = buy_cnt * float(amount)
                                
                                for x in df.index:
                                    print('■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■'
                                        ,df['market'][x] +' : '+self.getMarketName(df['market'][x])
                                        ,', PRICE:'
                                        ,'%12f' % amount
                                        ,'%12f' % df['trade_price'][x]
                                        ,', DIFF:'
                                        ,'%12f' % (float(df['trade_price'][x]) - float(amount))
                                        ,', RATE:'
                                        ,'% 4f' % (((float(df['trade_price'][x]) - float(amount)) /  float(amount) ) * 100)
                                        ,', INVESTMENT:'
                                        ,'%12f' % ((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))
                                        )

                                if (((float(df['trade_price'][x]) - float(check_amount)) /  float(check_amount) ) * 100) >= SELL_PLUS_RATE_3:
                                        check_amount = float(df['trade_price'][x])

                                if (((float(df['trade_price'][x]) - float(check_amount)) /  float(check_amount) ) * 100) <= SELL_MINUS_RATE_3:
                                        sell_amout =  (float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION )   
                                        print('#######################################################')
                                        print('### [SELL] ###',(float(amount) * buy_cnt) ,' - ', ((float(amount) * buy_cnt) * UPBIT_KRW_COMMISSION ) ,' = ', sell_amout)
                                        print('### [SELL] ###',(float(df['trade_price'][x]) * buy_cnt) ,' - ', ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ) ,' = ', sell_amout)
                                        print('#######################################################')
                                        # comm.log('[MINUS] '+self.getMarketName(df['market'][x])+' --- '+str(((float(df['trade_price'][x]) * buy_cnt) -  ((float(df['trade_price'][x]) * buy_cnt) * UPBIT_KRW_COMMISSION ))),'Y')
                                        investment_amount = investment_amount + sell_amout
                                        buymarket = []
                                        buy_cnt = 0
                                        buy_amount = 0
                                        sell_minus_count = sell_minus_count+1
                                        history_df =  pd.DataFrame()
                                        break

                                time.sleep(BUY_CHECK_TIME_SLEEP)
                    else:
                        logger.warning('ready ...')

                time.sleep(looptime)