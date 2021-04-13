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

from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import logging.config
from os import path

from trade import candles_mwd_data

##################################################
# constant

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vcts')

# candles_mwd_data
cmwd  = candles_mwd_data.MarketMonthWeekDayData()

##################################################

# main process

#################################################
# main
if __name__ == '__main__':
    # cmwd.load_candles_mwd_data()
        # cmwd.loadMarketSaveToDb()
        # cmwd.loadMarketCandlesMonthsSaveToDb()
        # cmwd.loadMarketCandlesWeeksSaveToDb()
        # cmwd.loadMarketCandlesDaysSaveToDb()

    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    columns = ['opening_price']
    cmwd.getContinueGrowthCoins("M",columns,"3")
    cmwd.getContinueGrowthCoins("W",columns,"4")
    cmwd.getContinueGrowthCoins("D",columns,"5")

    #scheduler = BlockingScheduler()
    #scheduler.add_job(main_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:d
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)    


