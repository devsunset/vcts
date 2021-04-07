# -*- coding: utf-8 -*-
##################################################
#
#         trade.py
#
##################################################

##################################################
# import

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

class Trade():
    # load market info save to db (vcts_meta table).
    def loadMarketSaveToDb(self):
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

            for data in data_json:
                data.setdefault('market_warning', '')
                sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning)'
                sqlText += ' values ("'+data.get('market')+'","'+data.get(
                    'korean_name')+'","'+data.get('english_name')+'","'+data.get('market_warning')+'")'
                comm.executeTxDB(conn, sqlText)

            conn.commit()
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()

    # get market date info
    def getMarkets(self):
        df = comm.searchDB("SELECT * FROM VCTS_META")
        # print(df)

        # for i in df.index:
        #     print(df['market'][i])
        return df

    # load market candles day info save to db (vcts_candles_day table).
    def loadMarketCandlesDaySaveToDb(self):
        logger.warn('loadMarketCandlesDaySaveToDb start')
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vcts_candles_day'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vcts_candles_day (market text, candle_date_time_utc text, candle_date_time_kst text, opening_price text, high_price text, low_price text, trade_price text, timestamp text, candle_acc_trade_price text, candle_acc_trade_volume text, prev_closing_price text, change_price text,  change_rate text, converted_trade_price text)'
            comm.executeTxDB(conn, sqlText)

            logger.warn('loadMarketCandlesDaySaveToDb db_init')

            markets = self.getMarkets()
            for i in markets.index:
                logger.warn(markets['market'][i])
                data_json = upbitapi.getQuotationCandlesDays(market=markets['market'][i],count=180,convertingPriceUnit='KRW')
                for data in data_json:                
                    sqlText = 'insert into vcts_candles_day  (market, candle_date_time_utc, candle_date_time_kst, opening_price, high_price, low_price, trade_price, timestamp, candle_acc_trade_price, candle_acc_trade_volume, prev_closing_price, change_price,  change_rate, converted_trade_price)'
                    sqlText += ' values ("'+data.get('market')+'","'+data.get('candle_date_time_utc')+'","'+data.get('candle_date_time_kst')+'","'+data.get('opening_price')+'","'+data.get('high_price')+'","'+data.get('low_price')+'","'+data.get('timestamp')+'","'+data.get('trade_price')+'","'+data.get('candle_acc_trade_price')+'","'+data.get('candle_acc_trade_volume')+'","'+data.get('prev_closing_price')+'","'+data.get('change_price')+'","'+data.get('change_rate')+'","'+data.get('converted_trade_price')+'")'
                    comm.executeTxDB(conn, sqlText)

            conn.commit()
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()        

    def test(self):
        pass
        '''
        print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 일(Day) 캔들 : getQuotationCandlesDays("KRW-BTC")')
        print(upbitapi.getQuotationCandlesDays(market='KRW-BTC',count=1,convertingPriceUnit='KRW'))
        
        print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 주(Week) 캔들 : getQuotationCandlesWeeks("KRW-BTC")')
        print(upbitapi.getQuotationCandlesWeeks('KRW-BTC'))

        print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 월(Month) 캔들 : getQuotationCandlesMonths("KRW-BTC")')
        print(upbitapi.getQuotationCandlesMonths('KRW-BTC'))
        '''