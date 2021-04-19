# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import hashlib
import json
import jwt
import requests
import time
from urllib.parse import urlencode
import uuid

class UpbitApi():
    """
    UPbit Api\n
    https://docs.upbit.com/reference
    https://api.upbit.com/v1
    """
    ###############################################################
    # INIT
    ###############################################################

    def __init__(self, access_key=None, secret=None, server_url=None):
        '''
        Constructor\n      
        access_key string : 발급 받은 acccess key\n
        secret string : 발급 받은 secret\n
        server_url string : server url - ex) https://api.upbit.com/v1 \n
        access_key, secret 값이 존재 해야 만 EXCHANGE API 사용 가능\n
        '''
        self.access_key = access_key
        self.secret = secret

        if server_url is None:
            self.server_url = 'https://api.upbit.com/v1'
        else:
            self.server_url = server_url

        self.markets = self.__markets_info()

    # ##############################################################
    #  HTTP REQUEST COMMON  FUNCTION
    # ##############################################################
    def __get(self, url, headers=None, data=None, params=None):
        resp = requests.get(url, headers=headers, data=data, params=params)
        if resp.status_code not in [200, 201]:
            logging.error('get(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                logging.error('resp: %s' % resp.text)
                if resp.status_code == 429 :
                    TOO_MANY_API_REQUESTS_INTERVAL = 0.5
                    while True:
                        time.sleep(TOO_MANY_API_REQUESTS_INTERVAL) 
                        TOO_MANY_API_REQUESTS_INTERVAL = TOO_MANY_API_REQUESTS_INTERVAL+0.5
                        resp = requests.get(url, headers=headers, data=data, params=params)
                        logging.error('Too many API Requests  retry: resp.status_code: %s' % resp.status_code)
                        if resp.status_code in [200, 201]:
                            return json.loads(resp.text)
                        elif resp.status_code != 429:           
                            logging.error('get(%s) failed(%d)' % (url, resp.status_code))                 
                            raise Exception('request.get() failed(%s)' % resp.text)
                else:                    
                    raise Exception('request.get() failed(%s)' % resp.text)
            raise Exception('request.get() failed(status_code:%d)' % resp.status_code)
        return json.loads(resp.text)

    def __post(self, url, headers, data):
        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code not in [200, 201]:
            logging.error('post(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                logging.error('resp: %s' % resp.text)
                if resp.status_code == 429 :
                    TOO_MANY_API_REQUESTS_INTERVAL = 0.5
                    while True:
                        time.sleep(TOO_MANY_API_REQUESTS_INTERVAL) 
                        TOO_MANY_API_REQUESTS_INTERVAL = TOO_MANY_API_REQUESTS_INTERVAL+0.5
                        resp = requests.post(url, headers=headers, data=data)
                        logging.error('Too many API Requests  retry: resp.status_code: %s' % resp.status_code)
                        if resp.status_code in [200, 201]:
                            return json.loads(resp.text)
                        elif resp.status_code != 429:           
                            logging.error('post(%s) failed(%d)' % (url, resp.status_code))                 
                            raise Exception('request.post() failed(%s)' % resp.text)
                else:                    
                    raise Exception('request.post() failed(%s)' % resp.text)
            raise Exception('request.post() failed(status_code:%d)' % resp.status_code)
        return json.loads(resp.text)

    def __delete(self, url, headers, data):
        resp = requests.delete(url, headers=headers, data=data)
        if resp.status_code not in [200, 201]:
            logging.error('delete(%s) failed(%d)' % (url, resp.status_code))
            if resp.text is not None:
                logging.error('resp: %s' % resp.text)
                if resp.status_code == 429 :
                    TOO_MANY_API_REQUESTS_INTERVAL = 0.5
                    while True:
                        time.sleep(TOO_MANY_API_REQUESTS_INTERVAL) 
                        TOO_MANY_API_REQUESTS_INTERVAL = TOO_MANY_API_REQUESTS_INTERVAL+0.5
                        resp = requests.delete(url, headers=headers, data=data)
                        logging.error('Too many API Requests  retry: resp.status_code: %s' % resp.status_code)
                        if resp.status_code in [200, 201]:
                            return json.loads(resp.text)
                        elif resp.status_code != 429:           
                            logging.error('delete(%s) failed(%d)' % (url, resp.status_code))                 
                            raise Exception('request.delete() failed(%s)' % resp.text)
                else:                    
                    raise Exception('request.delete() failed(%s)' % resp.text)
            raise Exception('request.delete() failed(status_code:%d)' % resp.status_code)
        return json.loads(resp.text)

    def __get_token(self, query):
        if query is not None:
            query_string = urlencode(query).encode()
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
        else:
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
            }
        return jwt.encode(payload, self.secret).decode('utf-8')

    def __get_headers(self, query=None):
        headers = {'Authorization': 'Bearer %s' % self.__get_token(query)}
        return headers

    ###############################################################
    # QUOTATION API
    ###############################################################
    # QUOTATION API - 시세 종목 조회 - 마켓 코드 조회
    def getQuotationMarketAll(self, isDetails=True):
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

        if isDetails not in [True, False]:
            logging.error('invalid isDetails: %s' % isDetails)
            raise Exception('invalid isDetails: %s' % isDetails)

        params = {'isDetails':  isDetails}

        return self.__get(URL, params=params)

    # QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들
    def getQuotationCandlesMinutes(self, unit, market, to=None, count=None):
        '''
        QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들\n
        https://docs.upbit.com/reference#%EB%B6%84minute-%EC%BA%94%EB%93%A4-1\n
        ******************************\n
        PATH PARAMS\n
        unit int32 : 분 단위. 가능한 값 : 1, 3, 5, 15, 10, 30, 60, 240\n
        ******************************\n    
        QUERY PARAMS\n
        market string : 마켓 코드 (ex. KRW-BTC, KRW-ETH)\n
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
        URL = self.server_url+'/candles/minutes/%s' % str(unit)

        if unit not in [1, 3, 5, 10, 15, 30, 60, 240]:
            logging.error('invalid unit: %s' % str(unit))
            raise Exception('invalid unit: %s' % str(unit))

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        if count is not None:
            if count not in list(range(1, 201)):
                logging.error('invalid count: %s' % str(count))
                raise Exception('invalid count: %s' % str(count))

        params = {'market': market}

        if to is not None:
            params['to'] = to

        if count is not None:
            params['count'] = count

        return self.__get(URL, params=params)

    # QUOTATION API - 시세 캔들 조회 - 일(Day) 캔들
    def getQuotationCandlesDays(self, market, to=None, count=None, convertingPriceUnit=None):
        '''
        QUOTATION API - 시세 캔들 조회 - 일(Day) 캔들\n
        https://docs.upbit.com/reference#%EC%9D%BCday-%EC%BA%94%EB%93%A4-1\n
        ******************************\n
        QUERY PARAMS\n
        market string : 마켓 코드 (ex. KRW-BTC, KRW-ETH)\n
        to string : 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들\n
        count int32 : 캔들 개수\n
        convertingPriceUnit string 종가 환산 화폐 단위 (생략 가능, KRW로 명시할 시 원화 환산 가격을 반환.)\n
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
        timestamp	마지막 틱이 저장된 시각	Long\n
        candle_acc_trade_price	누적 거래 금액	Double\n
        candle_acc_trade_volume	누적 거래량	Double\n
        prev_closing_price	전일 종가(UTC 0시 기준)	Double\n
        change_price	전일 종가 대비 변화 금액	Double\n
        change_rate	전일 종가 대비 변화량	Double\n
        converted_trade_price	종가 환산 화폐 단위로 환산된 가격(요청에 convertingPriceUnit 파라미터 없을 시 해당 필드 포함되지 않음.)	Double\n

        convertingPriceUnit 파라미터의 경우, 원화 마켓이 아닌 다른 마켓(ex. BTC, ETH)의 일봉 요청시 종가를\n
        명시된 파라미터 값으로 환산해 converted_trade_price 필드에 추가하여 반환합니다.\n
        현재는 원화(KRW) 로 변환하는 기능만 제공하며 추후 기능을 확장할 수 있습니다.
        '''
        URL = self.server_url+'/candles/days'

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        params = {'market': market}

        if to is not None:
            params['to'] = to

        if count is not None:
            params['count'] = count

        if convertingPriceUnit is not None:
            params['convertingPriceUnit'] = convertingPriceUnit

        return self.__get(URL, params=params)

    # QUOTATION API - 시세 캔들 조회 - 주(Week) 캔들
    def getQuotationCandlesWeeks(self, market, to=None, count=None):
        '''
        QUOTATION API - 시세 캔들 조회 - 주(Week) 캔들\n
        https://docs.upbit.com/reference#%EC%A3%BCweek-%EC%BA%94%EB%93%A4-1\n
        ******************************\n
        QUERY PARAMS\n
        market string : 마켓 코드 (ex. KRW-BTC, KRW-ETH)\n
        to string : 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들\n
        count int32 : 캔들 개수\n        
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
        timestamp	마지막 틱이 저장된 시각	Long\n
        candle_acc_trade_price	누적 거래 금액	Double\n
        candle_acc_trade_volume	누적 거래량	Double\n
        first_day_of_period	캔들 기간의 가장 첫 날	String
        '''
        URL = self.server_url+'/candles/weeks'

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        params = {'market': market}

        if to is not None:
            params['to'] = to

        if count is not None:
            params['count'] = count

        return self.__get(URL, params=params)

    # QUOTATION API - 시세 캔들 조회 - 월(Month) 캔들
    def getQuotationCandlesMonths(self, market, to=None, count=None):
        '''
        QUOTATION API - 시세 캔들 조회 - 월(Month) 캔들\n
        https://docs.upbit.com/reference#%EC%9B%94month-%EC%BA%94%EB%93%A4-1\n
        ******************************\n
        QUERY PARAMS\n
        market string : 마켓 코드 (ex. KRW-BTC, KRW-ETH)\n
        to string : 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들\n
        count int32 : 캔들 개수\n        
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
        timestamp	마지막 틱이 저장된 시각	Long\n
        candle_acc_trade_price	누적 거래 금액	Double\n
        candle_acc_trade_volume	누적 거래량	Double\n
        first_day_of_period	캔들 기간의 가장 첫 날	String
        '''
        URL = self.server_url+'/candles/months'

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        params = {'market': market}

        if to is not None:
            params['to'] = to

        if count is not None:
            params['count'] = count

        return self.__get(URL, params=params)

    # QUOTATION API - 시세 체결 조회 - 최근 체결 내역
    def getQuotationTradesTicks(self, market, to=None, count=None, cursor=None, daysAgo=None):
        '''
        QUOTATION API - 시세 체결 조회 - 최근 체결 내역\n
        https://docs.upbit.com/reference#%EC%B5%9C%EA%B7%BC-%EC%B2%B4%EA%B2%B0-%EB%82%B4%EC%97%AD\n
        ******************************\n
        QUERY PARAMS\n
        market string : 마켓 코드 (ex. KRW-BTC, KRW-ETH)\n
        to string : 마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ssXXX. 비워서 요청시 가장 최근 캔들\n
        count int32 : 체결 개수\n        
        cursor string 페이지네이션 커서 (sequentialId)\n
        daysAgo int32 최근 체결 날짜 기준 7일 이내의 이전 데이터 조회 가능. 비워서 요청 시 가장 최근 체결 날짜 반환. (범위: 1 ~ 7))\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        market	마켓 구분 코드	String\n
        trade_date_utc	체결 일자(UTC 기준)	String\n
        trade_time_utc	체결 시각(UTC 기준)	String\n
        timestamp	체결 타임스탬프	Long\n
        trade_price	체결 가격	Double\n
        trade_volume	체결량	Double\n
        prev_closing_price	전일 종가	Double\n
        change_price	변화량	Double\n
        ask_bid	매도/매수	String\n
        sequential_id	체결 번호(Unique)	Long\n
        sequential_id 필드는 체결의 유일성 판단을 위한 근거로 쓰일 수 있습니다. 하지만 체결의 순서를 보장하지는 못합니다.\n
        '''
        URL = self.server_url+'/trades/ticks'

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        if daysAgo is not None:
            if daysAgo not in [1, 2, 3, 4, 5, 6, 7]:
                logging.error('invalid daysAgo: %s' % str(daysAgo))
                raise Exception('invalid daysAgo: %s' % str(daysAgo))

        params = {'market': market}

        if to is not None:
            params['to'] = to

        if count is not None:
            params['count'] = count

        if cursor is not None:
            params['cursor'] = cursor

        if daysAgo is not None:
            params['daysAgo'] = daysAgo

        return self.__get(URL, params=params)

    # QUOTATION API - 시세 Ticker 조회 - 현재가 정보
    def getQuotationTicker(self, markets):
        '''
        QUOTATION API - 시세 Ticker 조회 - 현재가 정보\n
        요청 당시 종목의 스냅샷을 반환한다.\n
        https://docs.upbit.com/reference#ticker%ED%98%84%EC%9E%AC%EA%B0%80-%EB%82%B4%EC%97%AD\n
        ******************************\n
        QUERY PARAMS\n        
        markets array of strings  마켓 코드 목록 (ex. KRW-BTC,KRW-ETH)\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        market	종목 구분 코드	String\n
        trade_date	최근 거래 일자(UTC)	String\n
        trade_time	최근 거래 시각(UTC)	String\n
        trade_date_kst	최근 거래 일자(KST)	String\n
        trade_time_kst	최근 거래 시각(KST)	String\n
        opening_price	시가	Double\n
        high_price	고가	Double\n
        low_price	저가	Double\n
        trade_price	종가	Double\n
        prev_closing_price	전일 종가	Double\n
        change	EVEN : 보합\n
        RISE : 상승\n
        FALL : 하락	String\n
        change_price	변화액의 절대값	Double\n
        change_rate	변화율의 절대값	Double\n
        signed_change_price	부호가 있는 변화액	Double\n
        signed_change_rate	부호가 있는 변화율	Double\n
        trade_volume	가장 최근 거래량	Double\n
        acc_trade_price	누적 거래대금(UTC 0시 기준)	Double\n
        acc_trade_price_24h	24시간 누적 거래대금	Double\n
        acc_trade_volume	누적 거래량(UTC 0시 기준)	Double\n
        acc_trade_volume_24h	24시간 누적 거래량	Double\n
        highest_52_week_price	52주 신고가	Double\n
        highest_52_week_date	52주 신고가 달성일	String\n
        lowest_52_week_price	52주 신저가	Double\n
        lowest_52_week_date	52주 신저가 달성일	String\n
        timestamp	타임스탬프	Long
        '''
        URL = self.server_url+'/ticker'

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

    # QUOTATION API - 시세 호가 정보(Orderbook) 조회 - 호가 정보 조회
    def getQuotationOrderbook(self, markets):
        '''
        QUOTATION API - 시세 호가 정보(Orderbook) 조회 - 호가 정보 조회\n
        요청 당시 종목의 스냅샷을 반환한다.\n
        https://docs.upbit.com/reference#%ED%98%B8%EA%B0%80-%EC%A0%95%EB%B3%B4-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        QUERY PARAMS\n        
        markets array of strings  마켓 코드 목록 (ex. KRW-BTC,KRW-ETH)
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        market	마켓 코드	String\n
        timestamp	호가 생성 시각	Long\n
        total_ask_size	호가 매도 총 잔량	Double\n
        total_bid_size	호가 매수 총 잔량	Double\n
        orderbook_units	호가	List of Objects\n
        ask_price	매도호가	Double\n
        bid_price	매수호가	Double\n
        ask_size	매도 잔량	Double\n
        bid_size	매수 잔량	Double\n
        orderbook_unit 리스트에는 15호가 정보가 들어가며 차례대로 1호가, 2호가 ... 15호가의 정보를 담고 있습니다.\n
        '''
        URL = self.server_url+'/orderbook'

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

    ###############################################################
    # EXCHANGE API
    ###############################################################
    # EXCHANGE API - 자산 - 전체 계좌 조회
    def getExchangeAccounts(self):
        '''
        EXCHANGE API - 자산 - 전체 계좌 조회\n
        내가 보유한 자산 리스트를 보여줍니다.\n
        https://docs.upbit.com/reference#%EC%A0%84%EC%B2%B4-%EA%B3%84%EC%A2%8C-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        balance	주문가능 금액/수량	NumberString\n
        locked	주문 중 묶여있는 금액/수량	NumberString\n
        avg_buy_price	매수평균가	NumberString\n
        avg_buy_price_modified	매수평균가 수정 여부	Boolean\n
        unit_currency	평단가 기준 화폐	String\n
        '''
        URL = self.server_url+'/accounts'

        return self.__get(URL, self.__get_headers())

    # EXCHANGE API - 주문 - 주문 가능 정보
    def getExchangeOrdersChance(self, market):
        '''
        EXCHANGE API - 주문 - 주문 가능 정보\n        
        마켓별 주문 가능 정보를 확인한다.\n
        https://docs.upbit.com/reference#%EC%A3%BC%EB%AC%B8-%EA%B0%80%EB%8A%A5-%EC%A0%95%EB%B3%B4\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        market string  Market ID\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        bid_fee	매수 수수료 비율	NumberString\n
        ask_fee	매도 수수료 비율	NumberString\n
        market	마켓에 대한 정보	Object\n
        market.id	마켓의 유일 키	String\n
        market.name	마켓 이름	String\n
        market.order_types	지원 주문 방식	Array[String]\n
        market.order_sides	지원 주문 종류	Array[String]\n
        market.bid	매수 시 제약사항	Object\n
        market.bid.currency	화폐를 의미하는 영문 대문자 코드	String\n
        market.bit.price_unit	주문금액 단위	String\n
        market.bid.min_total	최소 매도/매수 금액	Number\n
        market.ask	매도 시 제약사항	Object\n
        market.ask.currency	화폐를 의미하는 영문 대문자 코드	String\n
        market.ask.price_unit	주문금액 단위	String\n
        market.ask.min_total	최소 매도/매수 금액	Number\n
        market.max_total	최대 매도/매수 금액	NumberString\n
        market.state	마켓 운영 상태	String\n
        bid_account	매수 시 사용하는 화폐의 계좌 상태	Object\n
        bid_account.currency	화폐를 의미하는 영문 대문자 코드	String\n
        bid_account.balance	주문가능 금액/수량	NumberString\n
        bid_account.locked	주문 중 묶여있는 금액/수량	NumberString\n
        bid_account.avg_buy_price	매수평균가	NumberString\n
        bid_account.avg_buy_price_modified	매수평균가 수정 여부	Boolean\n
        bid_account.unit_currency	평단가 기준 화폐	String\n
        ask_account	매도 시 사용하는 화폐의 계좌 상태	Object\n
        ask_account.currency	화폐를 의미하는 영문 대문자 코드	String\n
        ask_account.balance	주문가능 금액/수량	NumberString\n
        ask_account.locked	주문 중 묶여있는 금액/수량	NumberString\n
        ask_account.avg_buy_price	매수평균가	NumberString\n
        ask_account.avg_buy_price_modified	매수평균가 수정 여부	Boolean\n
        ask_account.unit_currency	평단가 기준 화폐	String\n
        '''
        URL = self.server_url + "/orders/chance"

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        data = {'market': market}

        return self.__get(URL, self.__get_headers(data), data)

    # EXCHANGE API - 주문 - 개별 주문 조회
    def getExchangeOrder(self, uuid=None, identifier=None):
        '''
        EXCHANGE API - 주문 - 개별 주문 조회\n        
        주문 UUID 를 통해 개별 주문건을 조회한다.\n
        https://docs.upbit.com/reference#%EA%B0%9C%EB%B3%84-%EC%A3%BC%EB%AC%B8-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        uuid string 주문 UUID\n
        identifier string 조회용 사용자 지정 값\n
        uuid 혹은 identifier 둘 중 하나의 값이 반드시 포함되어야 합니다.\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        uuid	주문의 고유 아이디	String\n
        side	주문 종류	String\n
        ord_type	주문 방식	String\n
        price	주문 당시 화폐 가격	NumberString\n
        state	주문 상태	String\n
        market	마켓의 유일키	String\n
        created_at	주문 생성 시간	DateString\n
        volume	사용자가 입력한 주문 양	NumberString\n
        remaining_volume	체결 후 남은 주문 양	NumberString\n
        reserved_fee	수수료로 예약된 비용	NumberString\n
        remaining_fee	남은 수수료	NumberString\n
        paid_fee	사용된 수수료	NumberString\n
        locked	거래에 사용중인 비용	NumberString\n
        executed_volume	체결된 양	NumberString\n
        trade_count	해당 주문에 걸린 체결 수	Integer\n
        trades	체결	Array[Object]\n
        trades.market	마켓의 유일 키	String\n
        trades.uuid	체결의 고유 아이디	String\n
        trades.price	체결 가격	NumberString\n
        trades.volume	체결 양	NumberString\n
        trades.funds	체결된 총 가격	NumberString\n
        trades.side	체결 종류	String\n
        trades.created_at	체결 시각	DateString\n
        '''
        URL = self.server_url+'/order'

        data = {}

        if uuid is not None:
            data['uuid'] = uuid

        if identifier is not None:
            data['identifier'] = identifier

        if len(data) == 0:
            logging.error('uuid  or identifier Either value must be included.')
            raise Exception(
                'uuid  or identifier Either value must be included.')

        return self.__get(URL, self.__get_headers(data), data)

    # EXCHANGE API - 주문 - 주문 리스트 조회
    def getExchangeOrders(self, market, state=None, page=1, order_by='desc', limit=100, states=None, uuids=None, identifiers=None):
        '''
        EXCHANGE API - 주문 - 주문 리스트 조회\n        
        주문 리스트를 조회한다.\n
        https://docs.upbit.com/reference#%EC%A3%BC%EB%AC%B8-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        market string Market ID\n
        state string 주문 상태\n
            - wait : 체결 대기 (default)\n
            - watch : 예약주문 대기\n
            - done : 전체 체결 완료\n
            - cancel : 주문 취소\n
        page int32 요청 페이지 , default: 1\n
        order_by string 정렬\n
            - asc : 오름차순\n
            - desc : 내림차순 (default)\n
        limit int32  요청 개수 (1 ~ 100) , default: 100\n
        states  array of strings  주문 상태 목록\n
            - 미체결 주문(wait, watch)과 완료 주문(done, cancel)은 혼합하여 조회하실 수 없습니다\n
            - 예시1) done, cancel 주문을 한 번에 조회 => 가능\n
            - 예시2) wait, done 주문을 한 번에 조회 => 불가능 (각각 API 호출 필요)\n
        uuids array of strings 주문 UUID의 목록\n
        identifiers array of strings 주문 identifier의 목록\n      
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        uuid	주문의 고유 아이디	String\n
        side	주문 종류	String\n
        ord_type	주문 방식	String\n
        price	주문 당시 화폐 가격	NumberString\n
        state	주문 상태	String\n
        market	마켓의 유일키	String\n
        created_at	주문 생성 시간	DateString\n
        volume	사용자가 입력한 주문 양	NumberString\n
        remaining_volume	체결 후 남은 주문 양	NumberString\n
        reserved_fee	수수료로 예약된 비용	NumberString\n
        remaining_fee	남은 수수료	NumberString\n
        paid_fee	사용된 수수료	NumberString\n
        locked	거래에 사용중인 비용	NumberString\n
        executed_volume	체결된 양	NumberString\n
        trade_count	해당 주문에 걸린 체결 수	Integer
        '''
        URL = self.server_url+'/orders'

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        if order_by not in ['asc', 'desc']:
            logging.error('invalid order_by: %s' % order_by)
            raise Exception('invalid order_by: %s' % order_by)

        if limit not in list(range(1, 101)):
            logging.error('invalid count: %s' % str(limit))
            raise Exception('invalid count: %s' % str(limit))

        if state is not None:
            if state not in ['wait', 'watch', 'done', 'cancel']:
                logging.error('invalid state: %s' % state)
                raise Exception('invalid state: %s' % state)

        if states is not None and len(states) > 0:
            type_temp = 1
            if states[0] == 'wait':
                type_temp = 1
            elif states[0] == 'watch':
                type_temp = 1
            elif states[0] == 'done':
                type_temp = 2
            else:
                type_temp = 2

            for s in states:
                if type_temp == 1:
                    if s not in ['wait', 'watch']:
                        logging.error('invalid state: %s' % s)
                        raise Exception('invalid state: %s' % s)
                else:
                    if s not in ['done', 'cancel']:
                        logging.error('invalid state: %s' % s)
                        raise Exception('invalid state: %s' % s)

        query = {
            'market': market,
            'page': page,
            'limit': limit,
            'order_by': order_by
        }

        if state is not None:
            query['state'] = state

        query_string = urlencode(query).encode()

        if states is not None:
            states_query_string = '&'.join(
                ["states[]={}".format(state_temp) for state_temp in states])
            query['states[]'] = states
            query_string = "{0}&{1}".format(query_string, states_query_string).encode()

        if uuids is not None:
            uuids_query_string = '&'.join(
                ["uuids[]={}".format(uuid) for uuid in uuids])
            query['uuids[]'] = uuids
            query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        if identifiers is not None:
            identifiers_query_string = '&'.join(
                ["identifiers[]={}".format(identifier) for uuid in identifiers])
            query['identifiers[]'] = identifiers
            query_string = "{0}&{1}".format(query_string, identifiers_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token.decode('utf-8')}

        return self.__get(URL, headers, query)

    # EXCHANGE API - 주문 - 주문 취소 접수
    def deleteExchangeOrder(self, uuid=None, identifier=None):
        '''
        EXCHANGE API - 주문 - 주문 취소 접수\n
        주문 UUID를 통해 해당 주문에 대한 취소 접수를 한다.\n
        https://docs.upbit.com/reference#%EC%A3%BC%EB%AC%B8-%EC%B7%A8%EC%86%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        uuid string 주문 UUID\n
        identifier string 조회용 사용자 지정 값\n
        uuid 혹은 identifier 둘 중 하나의 값이 반드시 포함되어야 합니다.\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        uuid	주문의 고유 아이디	String\n
        side	주문 종류	String\n
        ord_type	주문 방식	String\n
        price	주문 당시 화폐 가격	NumberString\n
        state	주문 상태	String\n
        market	마켓의 유일키	String\n
        created_at	주문 생성 시간	String\n
        volume	사용자가 입력한 주문 양	NumberString\n
        remaining_volume	체결 후 남은 주문 양	NumberString\n
        reserved_fee	수수료로 예약된 비용	NumberString\n
        remaing_fee	남은 수수료	NumberString\n
        paid_fee	사용된 수수료	NumberString\n
        locked	거래에 사용중인 비용	NumberString\n
        executed_volume	체결된 양	NumberString\n
        trade_count	해당 주문에 걸린 체결 수	Integer\n
        '''
        URL = self.server_url+'/order'

        data = {}

        if uuid is not None:
            data['uuid'] = uuid

        if identifier is not None:
            data['identifier'] = identifier

        if len(data) == 0:
            logging.error('uuid  or identifier Either value must be included.')
            raise Exception(
                'uuid  or identifier Either value must be included.')

        return self.__delete(URL, self.__get_headers(data), data)

    # EXCHANGE API - 주문 - 주문하기
    def postExchangeOrder(self, market, side, ord_type='limit', volume=None, price=None, dentifier=None):
        '''
        EXCHANGE API - 주문 - 주문하기\n
        주문 요청을 한다.\n
        https://docs.upbit.com/reference#%EC%A3%BC%EB%AC%B8%ED%95%98%EA%B8%B0\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        BODY PARAMS\n        
        market  string   Market ID\n
        side  string  주문 종류\n
            - bid : 매수\n
            - ask : 매도\n
        volume  string  주문 수량  (지정가, 시장가 매도 시 필수)\n
        price  string  유닛당 주문 가격 (지정가, 시장가 매수 시 필수)\n
            - ex) KRW-BTC 마켓에서 1BTC당 1,000 KRW로 거래할 경우, 값은 1000 이 된다.\n
            - ex) KRW-BTC 마켓에서 1BTC당 매도 1호가가 500 KRW 인 경우, 시장가 매수 시 값을 1000으로 세팅하면 2BTC가 매수된다.\n
            - (수수료가 존재하거나 매도 1호가의 수량에 따라 상이할 수 있음)\n
        ord_type  string  주문 타입\n
            - limit : 지정가 주문\n
            - price : 시장가 주문(매수)\n
            - market : 시장가 주문(매도)\n
        identifier string 조회용 사용자 지정 값\n

        🚧 원화 마켓 가격 단위를 확인하세요.\n
        원화 마켓에서 주문을 요청 할 경우, 원화 마켓 주문 가격 단위 를 확인하여 값을 입력해주세요.\n
        🚧 identifier 파라미터 사용\n
        identifier는 서비스에서 발급하는 uuid가 아닌 이용자가 직접 발급하는 키값으로, 주문을 조회하기 위해 할당하는 값입니다.\n
        해당 값은 사용자의 전체 주문 내 유일한 값을 전달해야하며, 비록 주문 요청시 오류가 발생하더라도 같은 값으로 다시 요청을 보낼 수 없습니다.\n
        주문의 성공 / 실패 여부와 관계없이 중복해서 들어온 identifier 값에서는 중복 오류가 발생하니, 매 요청시 새로운 값을 생성해주세요.\n
        🚧 시장가 주문\n
        시장가 주문은 ord_type 필드를 price or market 으로 설정해야됩니다.\n
        매수 주문의 경우 ord_type을 price로 설정하고 volume을 null 혹은 제외해야됩니다.\n
        매도 주문의 경우 ord_type을 market로 설정하고 price을 null 혹은 제외해야됩니다.\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        uuid	주문의 고유 아이디	String\n
        side	주문 종류	String\n
        ord_type	주문 방식	String\n
        price	주문 당시 화폐 가격	NumberString\n
        avg_price	체결 가격의 평균가	NumberString\n
        state	주문 상태	String\n
        market	마켓의 유일키	String\n
        created_at	주문 생성 시간	String\n
        volume	사용자가 입력한 주문 양	NumberString\n
        remaining_volume	체결 후 남은 주문 양	NumberString\n
        reserved_fee	수수료로 예약된 비용	NumberString\n
        remaining_fee	남은 수수료	NumberString\n
        paid_fee	사용된 수수료	NumberString\n
        locked	거래에 사용중인 비용	NumberString\n
        executed_volume	체결된 양	NumberString\n
        trade_count	해당 주문에 걸린 체결 수	Integer
        '''
        URL = self.server_url+'/orders'

        if market not in self.markets:
            logging.error('invalid market: %s' % market)
            raise Exception('invalid market: %s' % market)

        if side not in ['bid', 'ask']:
            logging.error('invalid side: %s' % side)
            raise Exception('invalid side: %s' % side)

        if ord_type not in ['limit', 'price', 'market']:
            logging.error('invalid ord_type: %s' % ord_type)
            raise Exception('invalid ord_type: %s' % ord_type)

        data = {
            'market': market,
            'side': side,
            'ord_type': ord_type
        }

        if ord_type == 'limit':
            if market.startswith('KRW') and not self.__is_valid_price(price):
                logging.error('invalid price: %.2f' % price)
                raise Exception('invalid price: %.2f' % price)

            if volume is None:
                logging.error('invalid volume: %.2f' % volume)
                raise Exception('invalid volume: %.2f' % volume)

            data['volume'] = str(volume)
            data['price'] = str(price)

        if ord_type == 'price':
            if market.startswith('KRW') and not self.__is_valid_price(price):
                logging.error('invalid price: %.2f' % price)
                raise Exception('invalid price: %.2f' % price)
            data['price'] = str(price)

        if ord_type == 'market':
            if volume is None:
                logging.error('invalid volume: %.2f' % volume)
                raise Exception('invalid volume: %.2f' % volume)
            data['volume'] = str(volume)

        return self.__post(URL, self.__get_headers(data), data)

    # EXCHANGE API - 출금 - 출금 리스트 조회
    def getExchangeWithdraws(self, currency, state, page=1, order_by='desc', limit=100, uuids=None, txids=None):
        '''
        EXCHANGE API - 출금 - 출금 리스트 조회\n        
        https://docs.upbit.com/reference#%EC%A0%84%EC%B2%B4-%EC%B6%9C%EA%B8%88-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        currency  string  Currency 코드\n
        state string 출금 상태\n
            - submitting : 처리 중\n
            - submitted : 처리 완료\n
            - almost_accepted : 출금대기중\n
            - rejected : 거부\n
            - accepted : 승인됨\n
            - processing : 처리 중\n
            - done : 완료\n
            - canceled : 취소됨\n
        uuids  array of strings   출금 UUID의 목록\n
        txids array of strings 출금 TXID의 목록\n
        limit int32 갯수 제한 (default: 100, max: 100)\n
        page   int32  페이지 수, default: 1\n
        order_by  string   정렬\n
            - asc : 오름차순\n
            - desc : 내림차순 (default)\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	출금의 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	출금의 트랜잭션 아이디	String\n
        state	출금 상태	String\n
        created_at	출금 생성 시간	DateString\n
        done_at	출금 완료 시간	DateString\n
        amount	출금 금액/수량	NumberString\n
        fee	출금 수수료	NumberString\n
        transaction_type	출금 유형\n
        default : 일반출금\n
        internal : 바로출금	String
        '''
        URL = self.server_url+'/withdraws'

        if currency is None:
            logging.error('invalid currency: %s' % currency)
            raise Exception('invalid currency: %s' % currency)

        if state is not None:
            if state not in ['submitting', 'submitted', 'almost_accepted', 'rejected', 'accepted', 'processing', 'done', 'canceled']:
                logging.error('invalid state: %s' % state)
                raise Exception('invalid state: %s' % state)

        if order_by not in ['asc', 'desc']:
            logging.error('invalid order_by: %s' % order_by)
            raise Exception('invalid order_by: %s' % order_by)

        if limit not in list(range(1, 101)):
            logging.error('invalid count: %s' % str(limit))
            raise Exception('invalid count: %s' % str(limit))

        query = {
            'currency': currency,
            'state': state,
            'page': page,
            'limit': limit,
            'order_by': order_by
        }

        query_string = urlencode(query).encode()

        if uuids is not None:
            uuids_query_string = '&'.join(
                ["uuids[]={}".format(uuid) for uuid in uuids])
            query['uuids[]'] = uuids
            query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        if txids is not None:
            txids_query_string = '&'.join(
                ["txids[]={}".format(txid) for txid in txids])
            query['txids[]'] = txids
            query_string = "{0}&{1}".format(query_string, txids_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        return self.__get(URL, headers, query)

    # EXCHANGE API - 출금 - 개별 출금 조회
    def getExchangeWithdraw(self, uuid=None, txid=None, currency=None):
        '''
        EXCHANGE API - 출금 - 개별 출금 조회\n        
        출금 UUID를 통해 개별 출금 정보를 조회한다.\n
        https://docs.upbit.com/reference#%EA%B0%9C%EB%B3%84-%EC%B6%9C%EA%B8%88-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        uuid  string  출금 UUID\n
        txid   string  출금 TXID\n
        currency  string Currency 코드\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	출금의 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	출금의 트랜잭션 아이디	String\n
        state	출금 상태	String\n
        created_at	출금 생성 시간	DateString\n
        done_at	출금 완료 시간	DateString\n
        amount	출금 금액/수량	NumberString\n
        fee	출금 수수료	NumberString\n
        transaction_type	출금 유형 String\n
            - default : 일반출금\n
            - internal : 바로출금	
        '''
        URL = self.server_url+'/withdraw'

        data = {}

        if uuid is not None:
            data['uuid'] = uuid

        if txid is not None:
            data['txid'] = txid

        if len(data) == 0:
            logging.error('uuid  or txid Either value must be included.')
            raise Exception('uuid  or txid Either value must be included.')

        if currency is not None:
            data['currency'] = currency

        return self.__get(URL, self.__get_headers(data), data)

    # EXCHANGE API - 출금 - 출금 가능 정보
    def getExchangeWithdrawsChance(self, currency):
        '''
        EXCHANGE API - 출금 - 출금 가능 정보\n        
        해당 통화의 가능한 출금 정보를 확인한다.\n
        https://docs.upbit.com/reference#%EC%B6%9C%EA%B8%88-%EA%B0%80%EB%8A%A5-%EC%A0%95%EB%B3%B4\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        currency  string Currency symbol\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        member_level	사용자의 보안등급 정보	Object\n
        member_level.security_level	사용자의 보안등급	Integer\n
        member_level.fee_level	사용자의 수수료등급	Integer\n
        member_level.email_verified	사용자의 이메일 인증 여부	Boolean\n
        member_level.identity_auth_verified	사용자의 실명 인증 여부	Boolean\n
        member_level.bank_account_verified	사용자의 계좌 인증 여부	Boolean\n
        member_level.kakao_pay_auth_verified	사용자의 카카오페이 인증 여부	Boolean\n
        member_level.locked	사용자의 계정 보호 상태	Boolean\n
        member_level.wallet_locked	사용자의 출금 보호 상태	Boolean\n
        currency	화폐 정보	Object\n
        currency.code	화폐를 의미하는 영문 대문자 코드	String\n
        currency.withdraw_fee	해당 화폐의 출금 수수료	NumberString\n
        currency.is_coin	화폐의 코인 여부	Boolean\n
        currency.wallet_state	해당 화폐의 지갑 상태	String\n
        currency.wallet_support	해당 화폐가 지원하는 입출금 정보	Array[String]\n
        account	사용자의 계좌 정보	Object\n
        account.currency	화폐를 의미하는 영문 대문자 코드	String\n
        account.balance	주문가능 금액/수량	NumberString\n
        account.locked	주문 중 묶여있는 금액/수량	NumberString\n
        account.avg_buy_price	매수평균가	NumberString\n
        account.avg_buy_price_modified	매수평균가 수정 여부	Boolean\n
        account.unit_currency	평단가 기준 화폐	String\n
        withdraw_limit	출금 제약 정보	Object\n
        withdraw_limit.currency	화폐를 의미하는 영문 대문자 코드	String\n
        withdraw_limit.minimum	출금 최소 금액/수량	NumberString\n
        withdraw_limit.onetime	1회 출금 한도	NumberString\n
        withdraw_limit.daily	1일 출금 한도	NumberString\n
        withdraw_limit.remaining_daily	1일 잔여 출금 한도	NumberString\n
        withdraw_limit.remaining_daily_krw	통합 1일 잔여 출금 한도	NumberString\n
        withdraw_limit.fixed	출금 금액/수량 소수점 자리 수	Integer\n
        withdraw_limit.can_withdraw	출금 지원 여부	Boolean
        '''
        URL = self.server_url+'/withdraws/chance'

        data = {'currency': currency}

        return self.__get(URL, self.__get_headers(data), data)

    # EXCHANGE API - 출금 - 코인 출금하기
    def postExchangeWithdrawsCoin(self, currency, amount, address, secondary_address=None, transaction_type='default'):
        '''
        EXCHANGE API - 출금 - 코인 출금하기\n        
        코인 출금을 요청한다.\n
        https://docs.upbit.com/reference#%EC%BD%94%EC%9D%B8-%EC%B6%9C%EA%B8%88%ED%95%98%EA%B8%B0\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        BODY PARAMS\n        
        currency  string  Currency symbol\n
        amount   string  출금 코인 수량\n
        address   string  출금 지갑 주소\n
        secondary_address  string  2차 출금주소 (필요한 코인에 한해서)\n
        transaction_type   string   출금 유형\n
            - default : 일반출금\n
            - internal : 바로출금\n
        바로출금 이용 시 유의사항\n
        업비트 회원의 주소가 아닌 주소로 바로출금을 요청하는 경우, 출금이 정상적으로 수행되지 않습니다. 반드시 주소를 확인 후 출금을 진행하시기 바랍니다.\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	출금의 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	출금의 트랜잭션 아이디	String\n
        state	출금 상태	String\n
        created_at	출금 생성 시간	DateString\n
        done_at	출금 완료 시간	DateString\n
        amount	출금 금액/수량	NumberString\n
        fee	출금 수수료	NumberString\n
        krw_amount	원화 환산 가격	NumberString\n
        transaction_type	출금 유형	String
        '''
        URL = self.server_url+'/withdraws/coin'

        if transaction_type not in ['default', 'internal']:
            logging.error('invalid transaction_type: %s' % transaction_type)
            raise Exception('invalid transaction_type: %s' % transaction_type)

        data = {
            'currency': currency,
            'amount': amount,
            'address': address,
            'transaction_type': transaction_type
        }

        if secondary_address is not None:
            data['secondary_address'] = secondary_address

        return self.__post(URL, self.__get_headers(data), data)

    # EXCHANGE API - 출금 - 원화 출금하기
    def postExchangeWithdrawsKrw(self,  amount):
        '''
        EXCHANGE API - 출금 - 원화 출금하기\n        
        원화 출금을 요청한다. 등록된 출금 계좌로 출금된다.\n
        https://docs.upbit.com/reference#%EC%9B%90%ED%99%94-%EC%B6%9C%EA%B8%88%ED%95%98%EA%B8%B0\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        BODY PARAMS\n        
        amount   string  출금 원화 수량\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	출금의 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	출금의 트랜잭션 아이디	String\n
        state	출금 상태	String\n
        created_at	출금 생성 시간	DateString\n
        done_at	출금 완료 시간	DateString\n
        amount	출금 금액/수량	NumberString\n
        fee	출금 수수료	NumberString\n
        transaction_type	출금 유형\n
        default : 일반출금\n
        internal : 바로출금	String
        '''
        URL = self.server_url+'/withdraws/krw'

        data = {'amount': amount}

        return self.__post(URL, self.__get_headers(data), data)

    # EXCHANGE API - 입금 - 입금 리스트 조회
    def getExchangeDeposits(self, currency, state, page=1, order_by='desc', limit=100, uuids=None, txids=None):
        '''
        EXCHANGE API - 입금 - 입금 리스트 조회\n        
        https://docs.upbit.com/reference#%EC%9E%85%EA%B8%88-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        currency  string  Currency 코드\n
        state string 입금 상태\n
            - submitting : 처리 중\n
            - submitted : 처리완료\n
            - almost_accepted : 입금 대기 중\n
            - rejected : 거절\n
            - accepted : 승인됨\n
            - processing : 처리 중\n
        uuids  array of strings   입금 UUID의 목록\n
        txids array of strings 입금 TXID의 목록\n
        limit int32 갯수 제한 (default: 100, max: 100)\n
        page   int32  페이지 수, default: 1\n
        order_by  string   정렬\n
            - asc : 오름차순\n
            - desc : 내림차순 (default)\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	입금에 대한 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	입금의 트랜잭션 아이디	String\n
        state	입금 상태	String\n
        created_at	입금 생성 시간	DateString\n
        done_at	입금 완료 시간	DateString\n
        amount	입금 수량	NumberString\n
        fee	입금 수수료	NumberString\n
        transaction_type	입금 유형\n
            - default : 일반입금\n
            - internal : 바로입금	String
        '''
        URL = self.server_url+'/deposits'

        if currency is None:
            logging.error('invalid currency: %s' % currency)
            raise Exception('invalid currency: %s' % currency)

        if state is not None:
            if state not in ['submitting', 'submitted', 'almost_accepted', 'rejected', 'accepted', 'processing']:
                logging.error('invalid state: %s' % state)
                raise Exception('invalid state: %s' % state)

        if order_by not in ['asc', 'desc']:
            logging.error('invalid order_by: %s' % order_by)
            raise Exception('invalid order_by: %s' % order_by)

        if limit not in list(range(1, 101)):
            logging.error('invalid count: %s' % str(limit))
            raise Exception('invalid count: %s' % str(limit))

        query = {
            'currency': currency,
            'state': state,
            'page': page,
            'limit': limit,
            'order_by': order_by
        }

        query_string = urlencode(query).encode()

        if uuids is not None:
            uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in uuids])
            query['uuids[]'] = uuids
            query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        if txids is not None:
            txids_query_string = '&'.join(["txids[]={}".format(txid) for txid in txids])
            query['txids[]'] = txids
            query_string = "{0}&{1}".format(query_string, txids_query_string).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        return self.__get(URL, headers, query)

    # EXCHANGE API - 입금 - 개별 입금 조회
    def getExchangeDeposit(self, uuid=None, txid=None, currency=None):
        '''
        EXCHANGE API - 입금 - 개별 입금 조회\n                
        https://docs.upbit.com/reference#%EA%B0%9C%EB%B3%84-%EC%9E%85%EA%B8%88-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n        
        uuid  string  입금 UUID\n
        txid   string  입금 TXID\n
        currency  string Currency 코드\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	입금에 대한 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	입금의 트랜잭션 아이디	String\n
        state	입금 상태	String\n
        created_at	입금 생성 시간	DateString\n
        done_at	입금 완료 시간	DateString\n
        amount	입금 수량	NumberString\n
        fee	입금 수수료	NumberString\n
        transaction_type	입금 유형 String\n
            - default : 일반입금\n
            - internal : 바로입금	
        '''
        URL = self.server_url+'/deposit'

        data = {}

        if uuid is not None:
            data['uuid'] = uuid

        if txid is not None:
            data['txid'] = txid

        if len(data) == 0:
            logging.error('uuid  or txid Either value must be included.')
            raise Exception('uuid  or txid Either value must be included.')

        if currency is not None:
            data['currency'] = currency

        return self.__get(URL, self.__get_headers(data), data)

        # EXCHANGE API - 입금 - 개별 입금 조회

    # EXCHANGE API - 입금 - 입금 주소 생성 요청
    def postExchangeDepositsGenerate_coin_address(self, currency):
        '''
        EXCHANGE API - 입금 - 입금 주소 생성 요청\n       
        입금 주소 생성을 요청한다.\n         
        https://docs.upbit.com/reference#%EC%9E%85%EA%B8%88-%EC%A3%BC%EC%86%8C-%EC%83%9D%EC%84%B1-%EC%9A%94%EC%B2%AD\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        BODY PARAMS\n                
        currency string Currency symbol\n
        ******************************\n
        RESPONSE1 \n
        필드	설명	타입\n
        success	요청 성공 여부	Boolean\n
        message	요청 결과에 대한 메세지	String\n
        RESPONSE2 \n
        필드	설명	타입\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        deposit_address	입금 주소	String\n
        secondary_address	2차 입금 주소	String\n
        입금 주소 생성 요청 API 유의사항\n
        입금 주소의 생성은 서버에서 비동기적으로 이뤄집니다.\n
        비동기적 생성 특성상 요청과 동시에 입금 주소가 발급되지 않을 수 있습니다.\n
        주소 발급 요청 시 결과로 Response1이 반환되며 주소 발급 완료 이전까지 계속 Response1이 반환됩니다.\n
        주소가 발급된 이후부터는 새로운 주소가 발급되는 것이 아닌 이전에 발급된 주소가 Response2 형태로 반환됩니다.\n
        정상적으로 주소가 생성되지 않는다면 일정 시간 이후 해당 API를 다시 호출해주시길 부탁드립니다.
        '''
        URL = self.server_url+'/deposits/generate_coin_address'

        data = {'currency': currency}

        return self.__post(URL, self.__get_headers(data), data)

    # EXCHANGE API - 입금 - 전체 입금 주소 조회
    def getExchangeDepositsCoin_addresses(self):
        '''
        EXCHANGE API - 입금 - 전체 입금 주소 조회\n
        내가 보유한 자산 리스트를 보여줍니다.\n
        https://docs.upbit.com/reference#%EC%A0%84%EC%B2%B4-%EC%9E%85%EA%B8%88-%EC%A3%BC%EC%86%8C-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n
        ******************************\n
        RESPONSE\n
        필드	설명	타입\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        deposit_address	입금 주소	String\n
        secondary_address	2차 입금 주소	String\n
        입금 주소 조회 요청 API 유의사항\n
        입금 주소 생성 요청 이후 아직 발급되지 않은 상태일 경우 deposit_address가 null일 수 있습니다.
        '''
        URL = self.server_url+'/deposits/coin_addresses'

        return self.__get(URL, self.__get_headers())

    # EXCHANGE API - 입금 - 개별 입금 주소 조회
    def getExchangeDepositsCoin_address(self, currency):
        '''
        EXCHANGE API - 입금 - 개별 입금 주소 조회\n               
        https://docs.upbit.com/reference#%EA%B0%9C%EB%B3%84-%EC%9E%85%EA%B8%88-%EC%A4%8F-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        QUERY PARAMS\n                
        currency string Currency symbol\n
        ******************************\n
        RESPONSE \n
        필드	설명	타입\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        deposit_address	입금 주소	String\n
        secondary_address	2차 입금 주소	String\n
        입금 주소 조회 요청 API 유의사항\n
        입금 주소 생성 요청 이후 아직 발급되지 않은 상태일 경우 deposit_address가 null일 수 있습니다.
        '''
        URL = self.server_url+'/deposits/coin_address'

        data = {'currency': currency}

        return self.__get(URL, self.__get_headers(data), data)

    # EXCHANGE API - 입금 - 원화 입금하기
    def postExchangeDepositsKrw(self, currency):
        '''
        EXCHANGE API - 입금 - 원화 입금하기\n       
        원화 입금을 요청한다.\n         
        https://docs.upbit.com/reference#%EC%9B%90%ED%99%94-%EC%9E%85%EA%B8%88%ED%95%98%EA%B8%B0\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n        
        ******************************\n
        BODY PARAMS\n                
        amount string 입금 원화 수량\n
        ******************************\n
        RESPONSE \n
        필드	설명	타입\n
        type	입출금 종류	String\n
        uuid	입금의 고유 아이디	String\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        txid	입금의 트랜잭션 아이디	String\n
        state	입금 상태	String\n
        created_at	입금 생성 시간	DateString\n
        done_at	입금 완료 시간	DateString\n
        amount	입금 금액/수량	NumberString\n
        fee	입금 수수료	NumberString\n
        transaction_type	트랜잭션 유형 String\n
            - default : 일반출금\n
            - internal : 바로출금	
        '''
        URL = self.server_url+'/deposits/krw'

        data = {'amount': amount}

        return self.__post(URL, self.__get_headers(data), data)

    # EXCHANGE API - 서비스 정보 - 입출금 현황
    def getExchangeStatusWallet(self):
        '''
        EXCHANGE API - 서비스 정보 - 입출금 현황\n
        입출금 현황 및 블록 상태를 조회합니다.\n
        https://docs.upbit.com/reference#%EC%9E%85%EC%B6%9C%EA%B8%88-%ED%98%84%ED%99%A9\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n
        ******************************\n
        입출금 현황 데이터는 실제 서비스 상태와 다를 수 있습니다.\n
        입출금 현황 API에서 제공하는 입출금 상태, 블록 상태 정보는 수 분 정도 지연되어 반영될 수 있습니다. \n
        본 API는 참고용으로만 사용하시길 바라며 실제 입출금을 수행하기 전에는 반드시 업비트 공지사항 및 입출금 현황 페이지를 참고해주시기 바랍니다.\n
        RESPONSE\n
        필드	설명	타입\n
        currency	화폐를 의미하는 영문 대문자 코드	String\n
        wallet_state	입출금 상태 String\n
            - working : 입출금 가능\n
            - withdraw_only : 출금만 가능\n
            - deposit_only : 입금만 가능\n
            - paused : 입출금 중단\n
            - unsupported : 입출금 미지원\n
        block_state	블록 상태 String\n
            - normal : 정상\n
            - delayed : 지연\n
            - inactive : 비활성 (점검 등)\n
        block_height	블록 높이	Integer\n
        block_updated_at	블록 갱신 시각	DateString\n
        '''
        URL = self.server_url+'/status/wallet'
        return self.__get(URL, self.__get_headers())

    # EXCHANGE API - 서비스 정보 - API 키 리스트 조회
    def getExchangeApiKeys(self):
        '''
        EXCHANGE API - 서비스 정보 - API 키 리스트 조회\n
        API 키 목록 및 만료 일자를 조회합니다.\n
        https://docs.upbit.com/reference#open-api-%ED%82%A4-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C\n
        ******************************\n
        HEADERS\n        
        Authorization string Authorization token (JWT)\n
        ******************************\n        
        RESPONSE\n
        필드	설명	타입\n
        access_key	access_key	String\n
        expire_at	expire_at String\
        '''
        URL = self.server_url+'/api_keys'
        return self.__get(URL, self.__get_headers())

    ###############################################################
    # ETC  FUNCTION
    # ##############################################################
    def __markets_info(self):
        try:
            market_all = self.getQuotationMarketAll()
            if market_all is None:
                return
            markets = []
            for market in market_all:
                markets.append(market['market'])
            return markets
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def __is_valid_price(self, price):
        '''
            https://docs.upbit.com/docs/market-info-trade-price-detail

            원화 마켓은 호가 별 주문 가격의 단위가 다릅니다. 아래 표를 참고하여 해당 단위로 주문하여 주세요.

            최소 호가 (이상)	최대 호가 (미만)	주문 가격 단위 (원)
            2,000,000		                                            1,000
            1,000,000	               2,000,000	               500
            500,000	                    1,000,000	                100
            100,000	                       500,000	                   50
            10,000	                        100,000	                    10
            1,000	                           10,000	                    5
            100	                                   1,000	                   1
            10	                                       100	                  0.1
            0	                                          10	              0.01
            예를 들어, 호가가 20,000원 일 경우 19,950원, 20,000원, 20,050원 으로 주문을 넣을 수 있으며,
            20,007원, 20,105원 등의 가격으로는 주문이 불가능 합니다.
        '''
        if price is None:
            return False
        elif price <= 10:
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
    # upbitapi  API TEST
    ###############################################################
    # upbitapi = upbitapi.UpbitApi()
    # upbitapi = upbitapi.UpbitApi(config.ACCESS_KEY,config.SECRET)

    # QUOTATION API TEST
    ###############################################################
    # print('■■■■■■■■■■ - QUOTATION API - 시세 종목 조회 - 마켓 코드 조회 : getQuotationMarketAll()')
    # print(upbitapi.getQuotationMarketAll())

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들 : getQuotationCandlesMinutes(1,"KRW-BTC")')
    # print(upbitapi.getQuotationCandlesMinutes(1,'KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 일(Day) 캔들 : getQuotationCandlesDays("KRW-BTC")')
    # print(upbitapi.getQuotationCandlesDays('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 주(Week) 캔들 : getQuotationCandlesWeeks("KRW-BTC")')
    # print(upbitapi.getQuotationCandlesWeeks('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 월(Month) 캔들 : getQuotationCandlesMonths("KRW-BTC")')
    # print(upbitapi.getQuotationCandlesMonths('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 체결 조회 - 최근 체결 내역 : getQuotationTradesTicks("KRW-BTC")')
    # print(upbitapi.getQuotationTradesTicks('KRW-BTC'))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 Ticker 조회 - 현재가 정보 : getQuotationTicker(["KRW-BTC","KRW-ETH"])')
    # print(upbitapi.getQuotationTicker(['KRW-BTC','KRW-ETH']))

    # print('■■■■■■■■■■ - QUOTATION API - 시세 호가 정보(Orderbook) 조회 - 호가 정보 조회 : getQuotationOrderbook(["KRW-BTC","KRW-ETH"])')
    # print(upbitapi.getQuotationOrderbook(['KRW-BTC','KRW-ETH']))

    # EXCHANGE API TEST (TO-DO)
    ###############################################################
    # print('■■■■■■■■■■ - EXCHANGE API - 자산 - 전체 계좌 조회 : getExchangeAccounts()')
    # print(upbitapi.getExchangeAccounts())

    # print('■■■■■■■■■■ - EXCHANGE API - 주문 - 주문 가능 정보 : getExchangeOrdersChance()')
    # print(upbitapi.getExchangeOrdersChance('KRW-BTC'))

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

    # print('■■■■■■■■■■ - EXCHANGE API - 서비스 정보 - 입출금 현황 : getExchangeStatusWallet()')
    # print(upbitapi.getExchangeStatusWallet())

    # print('■■■■■■■■■■ - EXCHANGE API - 서비스 정보 - API 키 리스트 조회 : getExchangeApiKeys()')
    # print(upbitapi.getExchangeApiKeys())

    print('upbitapi test completed ...')
