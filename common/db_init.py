# -*- coding: utf-8 -*-
##################################################
#
#                   db_init.py
#
##################################################

##################################################
#
# > seqlite3 install  && sqlite location PATH add
#
# > create table schema
#   - sqlite3 vcts.db
#
##################################################

##################################################
# import

import logging
import logging.config
from os import path
import sqlite3

from common import config
from common import common
# import config
# import common

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

common = common.Common()
##################################################

# db_init
def db_init():
    conn = None
    try:
        conn = sqlite3.connect(TARGET_DB)
        
        try:
            sqlText = 'drop table vcts_meta'
            common.executeTxDB(conn, sqlText)

            sqlText = 'drop table vcts_candles_day'
            common.executeTxDB(conn, sqlText)

            # sqlText = 'drop table vcts_candles_week'
            # common.executeTxDB(conn, sqlText)

            # sqlText = 'drop table vcts_candles_month'
            # common.executeTxDB(conn, sqlText)
        except Exception as e:
            logging.error(' Exception : %s' % e)
            pass

        sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name text, market_warning text)'
        common.executeTxDB(conn, sqlText)

        sqlText = 'create table vcts_candles_day (market text, candle_date_time_utc text, candle_date_time_kst text, opening_price text, high_price text, low_price text, trade_price text, timestamp text, candle_acc_trade_price text, candle_acc_trade_volume text, prev_closing_price text, change_price text,  change_rate text, converted_trade_price text)'
        common.executeTxDB(conn, sqlText)

        # sqlText = 'create table vcts_candles_week (market text, candle_date_time_utc text, candle_date_time_kst text, opening_price text, high_price text, low_price text, trade_price text, timestamp text, candle_acc_trade_price text, candle_acc_trade_volume text, first_day_of_period text)'
        # common.executeTxDB(conn, sqlText)

        # sqlText = 'create table vcts_candles_month (market  text, candle_date_time_utc text, candle_date_time_kst text, opening_price text, high_price text, low_price text, trade_price text, timestamp text, candle_acc_trade_price text, candle_acc_trade_volume text, first_day_of_period  text)'
        # common.executeTxDB(conn, sqlText)

        conn.commit()
    except Exception as e:
        logging.error(' Exception : %s' % e)
    finally:
        if conn is not None:
            conn.close()

    logger.warning('db_init completed...')

##################################################
# main
if __name__ == '__main__':
    db_init()
