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

from common import config
from common import common
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

#################################################
# main
if __name__ == '__main__':
    # moinitor markets info
    # vctstrade.monitorMarkets(loop=False, looptime=5, sort='signed_change_rate', targetMarket=['KRW'])

    # automatic trade1
    if config.EXECUTE_FUNCTION == 'automaticTrade_1':
        vctstrade.automaticTrade_1(looptime=5, period=12, targetMarket=['KRW'])

    # automatic trade 2
    if config.EXECUTE_FUNCTION == 'automaticTrade_2':
        vctstrade.automaticTrade_2(looptime=5, period=12, targetMarket=['KRW'])

    ###############################################

    # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()

    # scheduler = BlockingScheduler()
    # scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    # try:
    #    scheduler.start()
    # except Exception as err:
    #    logger.error(' main Exception : %s' % e) 