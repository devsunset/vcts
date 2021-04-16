# -*- coding: utf-8 -*-
##################################################
#
#         trade.py
#
##################################################

##################################################
# import
from pandas import DataFrame
import pandas as pd
import logging
import logging.config
from os import path
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

##################################################
# biz function

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 200)
pd.set_option('display.width', 200)

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
        markets = comm.searchDB("SELECT * FROM VCTS_META")
        return markets

    # get ticker markets
    def getTickerMarkets(self,markets):
        return pd.DataFrame(upbitapi.getQuotationTicker(markets))

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


