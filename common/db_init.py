##################################################
#
#          db_init 
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

import sqlite3
from common import constant
from common import common

##################################################
# constant

# target db
TARGET_DB = constant.TARGET_DB

##################################################

# db_init 
def db_init():
 try:
    conn = sqlite3.connect(TARGET_DB)
    try:
      sqlText = 'drop table vcts_meta'
      common.Common().executeTxDB(conn,sqlText)
    except Exception as err:
      print(err)
      pass

    sqlText = 'create table vcts_meta (id integer primary key autoincrement, market text , korean_name text, english_name, market_warning)'
    common.Common().executeTxDB(conn,sqlText)

    sqlText = 'insert into vcts_meta  (market,korean_name,english_name,market_warning) values ("KRW-BTC","비트코인","Bitcoin","")'
    common.Common().executeTxDB(conn,sqlText)
    conn.commit()
    conn.close()
 except Exception as err:
    print(err)

 print('db_init completed...')


##################################################
# main

if __name__ == '__main__':
    db_init()
