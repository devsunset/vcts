# -*- coding: utf-8 -*-
##################################################
#
#         trade.py
#
##################################################

##################################################
# import
from pandas import DataFrame
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

##################################################
# biz function

class MarketMonthWeekDayData():
    def load_candles_mwd_data(self):
        self.loadMarketSaveToDb()
        self.loadMarketCandlesMonthsSaveToDb()
        self.loadMarketCandlesWeeksSaveToDb()
        self.loadMarketCandlesDaysSaveToDb()

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

            comm.executeTxDB(conn, sqlText, sqlParam)
            conn.commit()
            logger.warn('loadMarketSaveToDb db_save')
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()

    # get market date info
    def getMarkets(self):        
        markets = comm.searchDB("SELECT * FROM VCTS_META")
        # print(markets)

        # for i in markets.index:
        #     print(markets['market'][i])
        return markets

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

    def test(self):
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
        where_query =""
        
        columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']

        date_info = comm.searchDB("select distinct first_day_of_period from  vcts_candles_months order by first_day_of_period asc")

        for i in date_info.index:
            print(i,date_info['first_day_of_period'][i])
            for c in columns:
                search_query +=", x"+str(i)+"."+c+" "

            join_query += " LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '"+date_info['first_day_of_period'][i]+"') x"+str(i)+" ON x"+str(i)+".market = a.market "


            

        sqlText = sqlText.replace("#__SEARCH_QUERY__#",search_query)
        sqlText = sqlText.replace("#__JOIN_QUERY__#",join_query)
        sqlText = sqlText.replace("#__WHERE_QUERY__#",where_query)

        print(sqlText)
        # print(search_query)
        # print(join_query)

        a = '''
        		SELECT  
                a.market, a.korean_name, a.eng_name
                , b.opening_price,c.opening_price, d.opening_price, e.opening_price ,f.opening_price, g.opening_price
                , b.trade_price, c.trade_price, d.trade_price, e.trade_price, f.trade_price, g.trade_price
                FROM
                vcts_meta a
                LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '2020-11-01') b ON b.market = a.market
                LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '2020-12-01') c ON c.market = a.market
                LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '2021-01-01') d ON d.market = a.market
                LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '2021-02-01') e ON e.market = a.market
                LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '2021-03-01') f ON f.market = a.market
                LEFT OUTER JOIN (select * from vcts_candles_months where first_day_of_period = '2021-04-01') g ON g.market = a.market
                WHERE  (c.opening_price > b.opening_price and d.opening_price > c.opening_price and e.opening_price > d.opening_price and f.opening_price > e.opening_price and g.opening_price > f.opening_price)
                AND (c.trade_price > b.trade_price and d.trade_price > c.trade_price and e.trade_price > d.trade_price and f.trade_price > e.trade_price and g.trade_price > f.trade_price)
        '''