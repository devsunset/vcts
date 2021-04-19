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
import time
import json

from trade import vcts_trade
from common import config
from common import common
from upbitapi import upbitapi


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

def monitorCoins():
    best = []
    
    ### TYPE ONE
    # markets = vctstrade.getMarkets()
    # for i in markets.index:
    #     best.append(markets['market'][i])

    ### TYPE TWO
    # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    # columns = ['opening_price','trade_price']
    # best = vctstrade.getChoiceGrowsMarkets(columns,3,3,3,3)

    # TYPE THREE 
    best.append('KRW-DOGE')

    ###########################################################################################
    while True:
        df = vctstrade.getTickerMarkets(best).sort_values(by='signed_change_rate', ascending=False)
        print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('%15s' % 'market'                
                ,'%7s' % 'change'
                ,'%12s' % '종가'
                ,'%13s' % '변화액'
                ,'%6s' % '변화율'
                ,'%13s' % '시가'
                ,'%13s' % '저가'
                ,'%13s' % '고가'
                ,'%7s' % '신고일'
                ,'%12s' % '신고가'
                ,'% 7s' % '신저일'
                ,'%12s' % '신저가'
                ,'%23s' %  'market'
                )
        print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        for x in df.index:
            print('%15s' % df['market'][x]
                ,'%6s' % df['change'][x]
                ,'%15f' % df['trade_price'][x]
                ,'%15f' % df['signed_change_price'][x]
                ,'%10f' % df['signed_change_rate'][x]
                ,'%15f' % df['opening_price'][x]
                ,'%15f' % df['low_price'][x]
                ,'%15f' % df['high_price'][x]
                ,'%10s' % df['highest_52_week_date'][x]
                ,'%15f' % df['highest_52_week_price'][x]
                ,'%10s' % df['lowest_52_week_date'][x]
                ,'%15f' % df['lowest_52_week_price'][x]
                ,'%20s' % vctstrade.getMarketName(df['market'][x])
                )
        time.sleep(3) 

def monitorConditionCoins():
    best = []

    ### TYPE ONE
    # markets = vctstrade.getMarkets()
    # for i in markets.index:
    #     best.append(markets['market'][i])

    ### TYPE TWO
    # get continue grows coins
    # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
    # columns = ['opening_price','trade_price']
    # best = vctstrade.getChoiceGrowsMarkets(columns,3,3,3,3)

    # TYPE THREE 
    best.append('KRW-AERGO')
    best.append('KRW-DOGE')

    ###########################################################################################


    while True:
        df = vctstrade.getTickerMarkets(best).sort_values(by='signed_change_rate', ascending=False)
        print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('%15s' % 'market'                
                ,'%7s' % 'change'
                ,'%12s' % '종가'
                ,'%13s' % '변화액'
                ,'%6s' % '변화율'
                ,'%11s' % '고가-종가'
                ,'%11s' % '고가-시가'
                ,'%11s' % '고가-저가'
                ,'%13s' % '시가'
                ,'%13s' % '저가'
                ,'%13s' % '고가'
                # ,'%7s' % '신고일'
                # ,'%12s' % '신고가'
                # ,'% 7s' % '신저일'
                # ,'%12s' % '신저가'
                ,'%23s' %  'market'
                )
        print('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        for x in df.index:
            if df['change'][x] != 'RISE' or str(df['market'][x])[0:4] != 'KRW-' or int(df['trade_price'][x]) > 1000 :
                continue

            print('%15s' % df['market'][x]
                ,'%6s' % df['change'][x]
                ,'%15f' % df['trade_price'][x]
                ,'%15f' % df['signed_change_price'][x]
                ,'%10f' % df['signed_change_rate'][x]
                ,'%15f' % (float(df['high_price'][x]) - float(df['trade_price'][x])) 
                ,'%15f' % (float(df['high_price'][x]) - float(df['opening_price'][x])) 
                ,'%15f' % (float(df['high_price'][x]) - float(df['low_price'][x])) 
                ,'%15f' % df['opening_price'][x]
                ,'%15f' % df['low_price'][x]
                ,'%15f' % df['high_price'][x]
                # ,'%10s' % df['highest_52_week_date'][x]
                # ,'%15f' % df['highest_52_week_price'][x]
                # ,'%10s' % df['lowest_52_week_date'][x]
                # ,'%15f' % df['lowest_52_week_price'][x]
                ,'%20s' % vctstrade.getMarketName(df['market'][x])
                )
        # break
        time.sleep(2) 

    ###########################################################################################


#################################################
# main
if __name__ == '__main__':
    # get candles chart data &  save to db
    # vctstrade.loadMarketsCandlesMwdData()
    
    # monitorCoins()

    # monitorConditionCoins()

    #scheduler = BlockingScheduler()
    #scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    #try:
    #    scheduler.start()
    #except Exception as err:
    #    logger.error(' main Exception : %s' % e)


    # upbitapi  API TEST
    ###############################################################
    # upbitapi = upbitapi.UpbitApi()
    upbitapi = upbitapi.UpbitApi(config.ACCESS_KEY,config.SECRET)

    # EXCHANGE API TEST (TO-DO)
    ###############################################################
    print('■■■■■■■■■■ - EXCHANGE API - 자산 - 전체 계좌 조회 : getExchangeAccounts()')
    print(upbitapi.getExchangeAccounts())

    print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문 가능 정보 : getExchangeOrdersChance()')
    print(upbitapi.getExchangeOrdersChance('KRW-AERGO'))

    # print('■■■■■■■■■■ - EXCHANGE API - 주문 - 개별 주문 조회 : getExchangeOrder(uuid)')
    # print(upbitapi.getExchangeOrder(uuid))

    # print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문 리스트 조회 : getExchangeOrders(market, state, page ,order_by)')
    # print(upbitapi.getExchangeOrders(market, state, page ,order_by))

    # print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문 취소 접수 : deleteExchangeOrder(uuid)')
    # print(upbitapi.deleteExchangeOrder(uuid))

    # print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문하기 : postExchangeOrder(market, side, volume, price, ord_type)')
    # print(upbitapi.postExchangeOrder(market, side, volume, price, ord_type))

    # print('■■■■■■■■■■ - EXCHANGE API - 출금 - 출금 리스트 조회 : getExchangeWithdraws(currency, state, page , order_by, limit, uuids, txids)')
    # print(upbitapi.getExchangeWithdraws(currency, state, page , order_by, limit, uuids, txids))

    # print('■■■■■■■■■■ - EXCHANGE API - 출금 - 개별 출금 조회 : getExchangeWithdraw(uuid, txid, currency)')
    # print(upbitapi.getExchangeWithdraw(uuid, txid, currency))

    # print('■■■■■■■■■■ - EXCHANGE API - 출금 - 출금 가능 정보 : getExchangeWithdrawsChance("BTC")')
    # print(upbitapi.getExchangeWithdrawsChance('BTC'))

    # print('■■■■■■■■■■ - EXCHANGE API - 출금 - 코인 출금하기 : postExchangeWithdrawsCoin(currency, amount, address)')
    # print(upbitapi.postExchangeWithdrawsCoin(currency, amount, address))

    # print('■■■■■■■■■■ - EXCHANGE API - 출금 - 원화 출금하기 : postExchangeWithdrawsKrw(amount)')
    # print(upbitapi.postExchangeWithdrawsKrw(amount))

    # print('■■■■■■■■■■ - EXCHANGE API - 입금 - 입금 리스트 조회 : getExchangeDeposits(currency, state, page , order_by, limit, uuids, txids)')
    # print(upbitapi.getExchangeDeposits(currency, state, page , order_by, limit, uuids, txids))

    # print('■■■■■■■■■■ - EXCHANGE API - 입금 - 개별 입금 조회 : getExchangeDeposit(uuid, txid, currency)')
    # print(upbitapi.getExchangeDeposit(uuid, txid, currency))

    # print('■■■■■■■■■■ - EXCHANGE API - 입금 - 입금 주소 생성 요청 : postExchangeDepositsGenerate_coin_address(currency)')
    # print(upbitapi.postExchangeDepositsGenerate_coin_address(currency))

    # print('■■■■■■■■■■ - EXCHANGE API - 입금 - 전체 입금 주소 조회 : getExchangeDepositsCoin_addresses()')
    # print(upbitapi.getExchangeDepositsCoin_addresses())

    # print('■■■■■■■■■■ - EXCHANGE API - 입금 - 개별 입금 주소 조회 : getExchangeDepositsCoin_address(currency)')
    # print(upbitapi.getExchangeDepositsCoin_address(currency))

    # print('■■■■■■■■■■ - EXCHANGE API - 입금 - 원화 입금하기 : postExchangeDepositsKrw(currency)')
    # print(upbitapi.postExchangeDepositsKrw(currency))

    print('■■■■■■■■■■ - EXCHANGE API - 서비스 정보 - 입출금 현황 : getExchangeStatusWallet()')
    print(upbitapi.getExchangeStatusWallet())

    print('■■■■■■■■■■ - EXCHANGE API - 서비스 정보 - API 키 리스트 조회 : getExchangeApiKeys()')
    print(upbitapi.getExchangeApiKeys())

    

    




  