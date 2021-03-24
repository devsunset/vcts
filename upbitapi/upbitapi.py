# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import json
import jwt
import requests
import time
from urllib.parse import urlencode

class UpbitApi():
    """
    UPbit Api\n
    https://docs.upbit.com/reference
    """

    ###############################################################
    # CONSTRUCTOR
    ###############################################################
    def __init__(self, access_key=None, secret=None):
        '''
        Constructor\n
        access_key, secret  이 없으면 인증가능 요청(EXCHANGE API)은 사용할 수 없음\n
        :param str access_key: 발급 받은 acccess key\n
        :param str secret: 발급 받은 secret\n
        '''
        self.access_key = access_key
        self.secret = secret
        self.remaining_req = dict()
        self.markets = self.__load_markets()

    ###############################################################
    # QUOTATION API
    ###############################################################
    def getMarketAll(self,isDetails=True):
        '''
        QUOTATION API - 시세 종목 조회 - 마켓 코드 조회\n
        ******************************\n
        업비트에서 거래 가능한 마켓 목록\n
        https://docs.upbit.com/reference#%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C \n
        ******************************\n
        QUERY PARAMS\n
        isDetails boolean   : 유의종목 필드과 같은 상세 정보 노출 여부(선택 파라미터) \n        
        ******************************\n
        RESPONSE\n
        필드명	설명	타입\n
        market	업비트에서 제공중인 시장 정보	String \n
        korean_name	거래 대상 암호화폐 한글명	String \n
        english_name	거래 대상 암호화폐 영문명	String \n
        market_warning	유의 종목 여부  NONE (해당 사항 없음), CAUTION(투자유의)	String 
        '''
        URL = 'https://api.upbit.com/v1/market/all'        

        if isDetails not in [True,False]:
            logging.error('invalid isDetails: %s' % isDetails)
            raise Exception('invalid isDetails: %s' % isDetails)
            
        params = {'isDetails':  isDetails}
        return self.__get(URL, params=params)

    def getCandlesMinutes(self, unit, market, to=None, count=None):
        '''
        QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들\n
        https://docs.upbit.com/reference#%EB%B6%84minute-%EC%BA%94%EB%93%A4-1\n
        ******************************\n
        PATH PARAMS\n
        unit int32 : 분 단위. 가능한 값 : 1, 3, 5, 15, 10, 30, 60, 240\n
        ******************************\n    
        QUERY PARAMS\n
        market string : 마켓 코드 (ex. KRW-BTC, BTC-BCC)\n
        to string : 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들\n
        count int32 : 캔들 개수(최대 200개까지 요청 가능)\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        market	마켓명	String\n
        candle_date_time_utc	캔들 기준 시각(UTC 기준)	String\n
        candle_date_time_kst	캔들 기준 시각(KST 기준)	String\n
        opening_price	시가	Double\n
        high_price	고가	Double\n
        low_price	저가	Double\n
        trade_price	종가	Double\n
        timestamp	해당 캔들에서 마지막 틱이 저장된 시각	Long\n
        candle_acc_trade_price	누적 거래 금액	Double\n
        candle_acc_trade_volume	누적 거래량	Double\n
        unit	분 단위(유닛)	Integer\n
        '''
        URL = 'https://api.upbit.com/v1/candles/minutes/%s' % str(unit)
        if unit not in [1, 3, 5, 10, 15, 30, 60, 240]:
            logging.error('invalid unit: %s' % str(unit))
            raise Exception('invalid unit: %s' % str(unit))
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)
        if count is not None:            
            if count not in list(range(1,201)):
                logging.error('invalid count: %s' % str(count))
                raise Exception('invalid count: %s' % str(count))

        params = {'market': market}
        if to is not None:
            params['to'] = to
        if count is not None:
            params['count'] = count
        return self.__get(URL, params=params)




    def getCandlesDays(self, market, to=None, count=None):
        '''
        QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들\n
        https://docs.upbit.com/reference#%EC%9D%BCday-%EC%BA%94%EB%93%A4-1
        :param str market: 마켓 코드 (ex. KRW-BTC, BTC-BCC)
        :param str to: 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들
        :param int count: 캔들 개수
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/candles/days'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        params = {'market': market}
        if to is not None:
            params['to'] = to
        if count is not None:
            params['count'] = count
        return self.__get(URL, params=params)

    def get_weeks_candles(self, market, to=None, count=None):
        '''
        주(Week) 캔들
        https://docs.upbit.com/v1.0/reference#%EC%A3%BCweek-%EC%BA%94%EB%93%A4-1
        :param str market: 마켓 코드 (ex. KRW-BTC, BTC-BCC)
        :param str to: 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들
        :param int count: 캔들 개수
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/candles/weeks'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)
        params = {'market': market}
        if to is not None:
            params['to'] = to
        if count is not None:
            params['count'] = count
        return self.__get(URL, params=params)

    def get_months_candles(self, market, to=None, count=None):
        '''
        월(Month) 캔들
        https://docs.upbit.com/v1.0/reference#%EC%9B%94month-%EC%BA%94%EB%93%A4-1
        :param str market: 마켓 코드 (ex. KRW-BTC, BTC-BCC)
        :param str to: 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들
        :param int count: 캔들 개수
        :return: json array
        '''

        URL = 'https://api.upbit.com/v1/candles/months'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)
        params = {'market': market}
        if to is not None:
            params['to'] = to
        if count is not None:
            params['count'] = count
        return self.__get(URL, params=params)

    def get_trades_ticks(self, market, to=None, count=None, cursor=None):
        '''
        당일 체결 내역
        https://docs.upbit.com/v1.0/reference#%EC%8B%9C%EC%84%B8-%EC%B2%B4%EA%B2%B0-%EC%A1%B0%ED%9A%8C
        :param str market: 마켓 코드 (ex. KRW-BTC, BTC-BCC)
        :param str to: 마지막 체결 시각. 형식 : [HHmmss 또는 HH:mm:ss]. 비워서 요청시 가장 최근 데이터
        :param int count: 체결 개수
        :param str cursor: 페이지네이션 커서 (sequentialId)
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/trades/ticks'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)
        params = {'market': market}
        if to is not None:
            params['to'] = to
        if count is not None:
            params['count'] = count
        if cursor is not None:
            params['cursor'] = cursor
        return self.__get(URL, params=params)

    def get_ticker(self, markets):
        '''
        현재가 정보
        요청 당시 종목의 스냅샷을 반환한다.
        https://docs.upbit.com/v1.0/reference#%EC%8B%9C%EC%84%B8-ticker-%EC%A1%B0%ED%9A%8C
        :param str[] markets: 마켓 코드 리스트 (ex. KRW-BTC, BTC-BCC)
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/ticker'
        if not isinstance(markets, list):
            logging.error('invalid parameter: markets should be list')
            raise Exception('invalid parameter: markets should be list')

        if len(markets) == 0:
            logging.error('invalid parameter: no markets')
            raise Exception('invalid parameter: no markets')

        for market in markets:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)

        markets_data = markets[0]
        for market in markets[1:]:
            markets_data += ',%s' % market
        params = {'markets': markets_data}
        return self.__get(URL, params=params)

    def get_orderbook(self, markets):
        '''
        호가 정보 조회
        https://docs.upbit.com/v1.0/reference#%ED%98%B8%EA%B0%80-%EC%A0%95%EB%B3%B4-%EC%A1%B0%ED%9A%8C
        :param str[] markets: 마켓 코드 목록 리스트 (ex. KRW-BTC,KRW-ADA)
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/orderbook?'
        if not isinstance(markets, list):
            logging.error('invalid parameter: markets should be list')
            raise Exception('invalid parameter: markets should be list')

        if len(markets) == 0:
            logging.error('invalid parameter: no markets')
            raise Exception('invalid parameter: no markets')

        for market in markets:
            if market not in self.markets:
                logging.error('invalid market: %s' % market)
                raise Exception('invalid market: %s' % market)

        markets_data = markets[0]
        for market in markets[1:]:
            markets_data += ',%s' % market
        params = {'markets': markets_data}
        return self.__get(URL, params=params)

    def get_remaining_req(self):
        '''
        요청 수 제한
        https://docs.upbit.com/docs/user-request-guide
        :return: dict
            ex) {'market': {'min': '582', 'sec': '2', 'update_time': datetime.datetime(2019, 6, 6, 7, 7, 12, 153219)}, 'candles': {'min': '592', 'sec': '6', 'update_time': datetime.datetime(2019, 6, 6, 7, 7, 12, 197177)}}
            - market 관련 요청은 2019년6월6일 7시7분12.153219초 이후 1분동안 582회, 1초동안 2회 호출 가능
            - candles 관련 요청은 2019년6월6일 7시7분12.197177초 이후 1분동안 592회, 1초동안 6회 호출 가능
        '''
        return self.remaining_req










    ###############################################################
    # EXCHANGE API
    ###############################################################
    """
    def get_accounts(self):
        '''
        전체 계좌 조회
        내가 보유한 자산 리스트를 보여줍니다.
        https://docs.upbit.com/v1.0/reference#%EC%9E%90%EC%82%B0-%EC%A0%84%EC%B2%B4-%EC%A1%B0%ED%9A%8C
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/accounts'
        return self.__get(URL, self.__get_headers())

    def get_chance(self, market):
        '''
        주문 가능 정보
        마켓별 주문 가능 정보를 확인한다.
        https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8-%EA%B0%80%EB%8A%A5-%EC%A0%95%EB%B3%B4
        :param str market: Market ID
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/orders/chance'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)
        data = {'market': market}
        return self.__get(URL, self.__get_headers(data), data)

    def get_order(self, uuid):
        '''
        개별 주문 조회
        주문 UUID 를 통해 개별 주문건을 조회한다.
        https://docs.upbit.com/v1.0/reference#%EA%B0%9C%EB%B3%84-%EC%A3%BC%EB%AC%B8-%EC%A1%B0%ED%9A%8C
        :param str uuid: 주문 UUID
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/order'
        try:
            data = {'uuid': uuid}
            return self.__get(URL, self.__get_headers(data), data)
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def get_orders(self, market, state, page=1, order_by='asc'):
        '''
        주문 리스트 조회
        주문 리스트를 조회한다.
        https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C
        :param str market: Market ID
        :param str state: 주문 상태
            wait:체결 대기(default)
            done: 체결 완료
            cancel: 주문 취소
        :param int page: 페이지 수, default: 1
        :param str order_by: 정렬 방식
            asc: 오름차순(default)
            desc:내림차순
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/orders'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        if state not in ['wait', 'done', 'cancel']:
            logging.error('invalid state: %s' % state)
            raise Exception('invalid state: %s' % state)

        if order_by not in ['asc', 'desc']:
            logging.error('invalid order_by: %s' % order_by)
            raise Exception('invalid order_by: %s' % order_by)

        data = {
            'market': market,
            'state': state,
            'page': page,
            'order_by': order_by
        }
        return self.__get(URL, self.__get_headers(data), data)

    def order(self, market, side, volume, price):
        '''
        주문하기
        주문 요청을 한다.
        https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8%ED%95%98%EA%B8%B0-1
        :param str market: 마켓 ID (필수)
        :param str side: 주문 종류 (필수)
            bid : 매수
            ask : 매도
        :param str volume: 주문량 (필수)
        :param str price: 유닛당 주문 가격. (필수)
            ex) KRW-BTC 마켓에서 1BTC당 1,000 KRW로 거래할 경우, 값은 1000 이 된다.
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/orders'
        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        if side not in ['bid', 'ask']:
            logging.error('invalid side: %s' % side)
            raise Exception('invalid side: %s' % side)

        if market.startswith('KRW') and not self.__is_valid_price(price):
            logging.error('invalid price: %.2f' % price)
            raise Exception('invalid price: %.2f' % price)

        data = {
            'market': market,
            'side': side,
            'volume': str(volume),
            'price': str(price),
            'ord_type': 'limit'
        }
        return self.__post(URL, self.__get_headers(data), data)

    def cancel_order(self, uuid):
        '''
        주문 취소
        주문 UUID를 통해 해당 주문을 취소한다.
        https://docs.upbit.com/v1.0/reference#%EC%A3%BC%EB%AC%B8-%EC%B7%A8%EC%86%8C
        :param str uuid: 주문 UUID
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/order'
        data = {'uuid': uuid}
        return self.__delete(URL, self.__get_headers(data), data)

    def get_withraws(self, currency, state, limit):
        '''
        출금 리스트 조회
        https://docs.upbit.com/v1.0/reference#%EC%A0%84%EC%B2%B4-%EC%B6%9C%EA%B8%88-%EC%A1%B0%ED%9A%8C
        :param str currency: Currency 코드
        :param str state: 출금 상태
            submitting : 처리 중
            submitted : 처리 완료
            almost_accepted : 출금대기중
            rejected : 거부
            accepted : 승인됨
            processing : 처리 중
            done : 완료
            canceled : 취소됨
        :param int limit: 갯수 제한
        :return: json array
        '''
        LIMIT_MAX = 100
        VALID_STATE = ['submitting', 'submitted', 'almost_accepted',
                       'rejected', 'accepted', 'processing', 'done', 'canceled']
        URL = 'https://api.upbit.com/v1/withdraws'
        data = {}
        if currency is not None:
            data['currency'] = currency
        if state is not None:
            if state not in VALID_STATE:
                logging.error('invalid state(%s)' % state)
                raise Exception('invalid state(%s)' % state)
            data['state'] = state
        if limit is not None:
            if limit <= 0 or limit > LIMIT_MAX:
                logging.error('invalid limit(%d)' % limit)
                raise Exception('invalid limit(%d)' % limit)
            data['limit'] = limit
        return self.__get(URL, self.__get_headers(data), data)

    def get_withraw(self, uuid):
        '''
        개별 출금 조회
        출금 UUID를 통해 개별 출금 정보를 조회한다.
        https://docs.upbit.com/v1.0/reference#%EA%B0%9C%EB%B3%84-%EC%B6%9C%EA%B8%88-%EC%A1%B0%ED%9A%8C
        :param str uuid: 출금 UUID
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/withdraw'
        data = {'uuid': uuid}
        return self.__get(URL, self.__get_headers(data), data)

    def get_withraws_chance(self, currency):
        '''
        출금 가능 정보
        해당 통화의 가능한 출금 정보를 확인한다.
        https://docs.upbit.com/v1.0/reference#%EC%B6%9C%EA%B8%88-%EA%B0%80%EB%8A%A5-%EC%A0%95%EB%B3%B4
        :param str currency: Currency symbol
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/withdraws/chance'
        data = {'currency': currency}
        return self.__get(URL, self.__get_headers(data), data)

    def withdraws_coin(self, currency, amount, address, secondary_address=None):
        '''
        코인 출금하기
        코인 출금을 요청한다.
        https://docs.upbit.com/v1.0/reference#%EC%BD%94%EC%9D%B8-%EC%B6%9C%EA%B8%88%ED%95%98%EA%B8%B0
        :param str currency: Currency symbol
        :param str amount: 출금 코인 수량
        :param str address: 출금 지갑 주소
        :param str secondary_address: 2차 출금 주소 (필요한 코인에 한해서)
        '''
        URL = 'https://api.upbit.com/v1/withdraws/coin'
        data = {
            'currency': currency,
            'amount': amount,
            'address': address
        }
        if secondary_address is not None:
            data['secondary_address'] = secondary_address
        return self.__post(URL, self.__get_headers(data), data)

    def withdraws_krw(self, amount):
        '''
        원화 출금하기
        원화 출금을 요청한다. 등록된 출금 계좌로 출금된다.
        https://docs.upbit.com/v1.0/reference#%EC%9B%90%ED%99%94-%EC%B6%9C%EA%B8%88%ED%95%98%EA%B8%B0
        :param str amount: 출금 원화 수량
        '''
        URL = 'https://api.upbit.com/v1/withdraws/krw'
        data = {'amount': amount}
        return self.__post(URL, self.__get_headers(data), data)

    def get_deposits(self, currency=None, limit=None, page=None, order_by=None):
        '''
        입금 리스트 조회
        https://docs.upbit.com/v1.0/reference#%EC%9E%85%EA%B8%88-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C
        :param str currency: Currency 코드
        :param int limit: 페이지당 개수
        :param int page: 페이지 번호
        :param str order_by: 정렬 방식
        :return: json array
        '''
        URL = 'https://api.upbit.com/v1/deposits'
        data = {}
        if currency is not None:
            data['currency'] = currency
        if limit is not None:
            data['limit'] = limit
        if page is not None:
            data['page'] = page
        if order_by is not None:
            data['order_by'] = order_by
        return self.__get(URL, self.__get_headers(data), data)

    def get_deposit(self, uuid):
        '''
        개별 입금 조회
        https://docs.upbit.com/v1.0/reference#%EA%B0%9C%EB%B3%84-%EC%9E%85%EA%B8%88-%EC%A1%B0%ED%9A%8C
        :param str uuid: 개별 입금의 UUID
        :return: json object
        '''
        URL = 'https://api.upbit.com/v1/deposit'
        data = {'uuid': uuid}
        return self.__get(URL, self.__get_headers(data), data)
 """

    ###############################################################
    #  HTTP REQUEST COMMON  FUNCTION
    # ##############################################################

    def __get(self, url, headers=None, data=None, params=None):
        resp = requests.get(url, headers=headers, data=data, params=params)
        if resp.status_code not in [200, 201]:
            logging.error('get(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                logging.error('resp: %s' % resp.text)
                raise Exception('request.get() failed(%s)' % resp.text)
            raise Exception(
                'request.get() failed(status_code:%d)' % resp.status_code)
        self.__update_remaining_req(resp)
        return json.loads(resp.text)

    def __post(self, url, headers, data):
        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code not in [200, 201]:
            logging.error('post(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                raise Exception('request.post() failed(%s)' % resp.text)
            raise Exception(
                'request.post() failed(status_code:%d)' % resp.status_code)
        self.__update_remaining_req(resp)
        return json.loads(resp.text)

    def __delete(self, url, headers, data):
        resp = requests.delete(url, headers=headers, data=data)
        if resp.status_code not in [200, 201]:
            logging.error('delete(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                raise Exception('request.delete() failed(%s)' % resp.text)
            raise Exception(
                'request.delete() failed(status_code:%d)' % resp.status_code)
        self.__update_remaining_req(resp)
        return json.loads(resp.text)

    def __get_token(self, query):
        payload = {
            'access_key': self.access_key,
            'nonce': int(time.time() * 1000),
        }
        if query is not None:
            payload['query'] = urlencode(query)
        return jwt.encode(payload, self.secret, algorithm='HS256').decode('utf-8')

    def __get_headers(self, query=None):
        headers = {'Authorization': 'Bearer %s' % self.__get_token(query)}
        return headers

    ###############################################################
    # ETC  FUNCTION
    # ##############################################################
    def __load_markets(self):
        try:
            market_all = self.getMarketAll()
            if market_all is None:
                return
            markets = []
            for market in market_all:
                markets.append(market['market'])
            return markets
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def __update_remaining_req(self, resp):
        if 'Remaining-Req' not in resp.headers.keys():
            return None
        keyvals = resp.headers['Remaining-Req'].split('; ')
        group = None
        keyval = dict()
        for _keyval in keyvals:
            kv = _keyval.split('=')
            if kv[0] == 'group':
                group = kv[1]
            else:
                keyval[kv[0]] = kv[1]
        if group is None:
            return
        keyval['update_time'] = datetime.now()
        self.remaining_req[group] = keyval

    def __is_valid_price(self, price):
        '''
        원화 마켓 주문 가격 단위
        원화 마켓은 호가 별 주문 가격의 단위가 다릅니다. 아래 표를 참고하여 해당 단위로 주문하여 주세요.
        https://docs.upbit.com/v1.0/docs/%EC%9B%90%ED%99%94-%EB%A7%88%EC%BC%93-%EC%A3%BC%EB%AC%B8-%EA%B0%80%EA%B2%A9-%EB%8B%A8%EC%9C%84
        ~10         : 0.01
        ~100        : 0.1
        ~1,000      : 1
        ~10,000     : 5
        ~100,000    : 10
        ~500,000    : 50
        ~1,000,000  : 100
        ~2,000,000  : 500
        +2,000,000  : 1,000
        '''
        if price <= 10:
            if (price*100) != int(price*100):
                return False
        elif price <= 100:
            if (price*10) != int(price*10):
                return False
        elif price <= 1000:
            if price != int(price):
                return False
        elif price <= 10000:
            if (price % 5) != 0:
                return False
        elif price <= 100000:
            if (price % 10) != 0:
                return False
        elif price <= 500000:
            if (price % 50) != 0:
                return False
        elif price <= 1000000:
            if (price % 100) != 0:
                return False
        elif price <= 2000000:
            if (price % 500) != 0:
                return False
        elif (price % 1000) != 0:
            return False
        return True


#################################################
# main
if __name__ == '__main__':

    upbitapi = UpbitApi()
    
    # print('QUOTATION API - 시세 종목 조회 - 마켓 코드 조회 : getMarketAll()')
    # print(upbitapi.getMarketAll())

    # print('QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들 : getCandlesMinutes(1,"KRW-BTC")')
    # print(upbitapi.getCandlesMinutes(1,'KRW-BTC'))

    print('QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들 : getCandlesMinutes(1,"KRW-BTC")')
    print(upbitapi.getCandlesMinutes(1,'KRW-BTC'))

