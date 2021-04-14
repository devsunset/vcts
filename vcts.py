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
# biz function

def getGrowsCoins(m=2,w=2,d=2,count=1):
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    columns = ['opening_price','trade_price']
    coinsMonth = cmwd.getContinueGrowthCoins("M",columns,str(m))
    coinsWeek = cmwd.getContinueGrowthCoins("W",columns,str(w))
    coinsDay = cmwd.getContinueGrowthCoins("D",columns,str(d))

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

#################################################
# main
if __name__ == '__main__':
    # 1.get candles chart data &  save to db
    # cmwd.load_candles_mwd_data()
    
    # 2.get continue grows coins
    best = getGrowsCoins(3,3,3,3)

    # 3. get candles detail data
    for b in best:
        print(b)

    #scheduler = BlockingScheduler()
    #scheduler.add_job(main_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)

    

    




  