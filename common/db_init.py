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
        except Exception as e:
            logging.error(' Exception : %s' % e)
            pass

        sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name, market_warning)'
        common.executeTxDB(conn, sqlText)

        sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning) values ("KRW-BTC","비트코인","Bitcoin","")'
        common.executeTxDB(conn, sqlText)
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
