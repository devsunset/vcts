# -*- coding: utf-8 -*-
##################################################
#
#                   config.py
#
##################################################

# 프로그램 실행 주기 
INTERVAL_SECONDS = 60

# target db
TARGET_DB = 'db/local.db'

# telegram token
TELEGRAM_TOKEN = '1280370073:AAHFwcNtcS9pvqF29zJJKEOY0SvnW8NH1do'

# telegram chat_id
TELEGRAM_CHAT_ID = 1203202572

# access key
ACCESS_KEY=''

# secret
SECRET = ''


##################################################

EXECUTE_FUNCTION = 'automaticTrade'
LOOPTIME = 1
PERIOD = 30 
MAX_TRADE_PRICE = 10000
UPBIT_KRW_COMMISSION = 0.005
CHECK_TIME_SLEEP = 1
ASK_BID_CHECK_COUNT = 30
ASK_BID_CHECK_TYPE = 'count'

# LOCAL
# INIT_INVESTMENT = 200000
# SELL_STOP_SLEEP_TIME = 30
# TARGET_PUMP_RATE = 4.5
# TARGET_BUY_RATE = 0.5
# SELL_PLUS_RATE = 0.5
# SELL_PLUS_MAX_RATE = 1.5
# SELL_MINUS_RATE = -1.0
# SELL_MINUS_MAX_RATE = -1.5

# REAL
INIT_INVESTMENT = 200000
SELL_STOP_SLEEP_TIME = 600
TARGET_PUMP_RATE = 5.0
TARGET_BUY_RATE = 4.5
SELL_PLUS_RATE = 0.5
SELL_PLUS_MAX_RATE = 13.5
SELL_MINUS_RATE = -1.5
SELL_MINUS_MAX_RATE = -3.5

##################################################

# candles  count
CANDLES_DAY_COUNT = 180
CANDLES_WEEK_COUNT = 26
CANDLES_MONTH_COUNT = 6

# converting Price Unit
CONVERTING_PRICE_UNIT = 'KRW'
