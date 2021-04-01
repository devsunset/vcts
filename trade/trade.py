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
        market_dict = upbitapi.getQuotationMarketAll()

        try:
            conn = sqlite3.connect(TARGET_DB)

            try:
                sqlText = 'drop table vcts_meta'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name text, market_warning text)'
            comm.executeTxDB(conn, sqlText)

            for data in market_dict:
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

    def getMarkets(self):
        df = comm.searchDB("SELECT * FROM VCTS_META")
        print(df)

        # for i in df.index:
        #     print(df['market'][i])
