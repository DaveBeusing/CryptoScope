#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#



import pandas as pd
from time import sleep
from datetime import datetime
from os.path import dirname, abspath
from binance.exceptions import BinanceAPIException

from cryptoscope import Config


def getPath():
    ''' Returns the current script path
    '''
    #return os.path.dirname( os.path.abspath( __file__ ) )
    return dirname( abspath( __file__ ) )


def log( data, timestamp=True ):
    with open( Config.Logfile, 'a+' ) as fd:
        if timestamp:
            fd.write( f'{str(datetime.now())} {data}\n' )
        else:
            fd.write( f'{data}\n' )




def fetch_NonLeveragedTradePairs( client, quoteAsset='USDT', streamFormat=None ):
    ''' Return a List of Non Leveraged Trade Pairs

    :param client       -> binance.Client object
    :param quoteAsset   -> type:str: Symbol of quote Asset
    :return List
    '''
    data = client.get_exchange_info()
    symbols = [ x['symbol'] for x in data['symbols'] ]
    # leveraged tokens contain UP/DOWN BULL/BEAR in name
    # Was ist mit FIAT paaren -> EUR/USDT, AUD, BIDR, BRL, GBP, RUB, TRY, TUSD, USDC, DAI. IDTZ, UAH, NGN, VAI, USDP 'EUR', 'GBP', 'USD', 'AUD', 'JPY', 'RUB'
    exclude_pairs = [ 'UP', 'DOWN', 'BEAR', 'BULL' ] 
    non_pairs = [ symbol for symbol in symbols if all( excludes not in symbol for excludes in exclude_pairs ) ]
    pairs = [ symbol for symbol in non_pairs if symbol.endswith( quoteAsset ) ]

    if streamFormat is not None:
        pairs = [ i.lower() + streamFormat for i in pairs ]

    return pairs


def fetch_OHLCV( client, symbol, interval='1d', start_date='1 day ago UTC', end_date=None ):    
    '''Fetch historical kline data (Candlesticks)
    
    https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
    
    :param client   -> binance.Client object
    :param symbol   -> type:str: Name of symbol pair e.g BTCUSDT
    :param interval -> type:str: Data interval e.g. 1m | 3m | 5m | 15m | 30m | 1h | 2h | 4h | 6h | 8h | 12h | 1d | 3d | 1W | 1M
    :param start    -> type:str|int: Start date string in UTC format or timestamp in milliseconds
    :param end      -> type:str|int: (optional) - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
    :return DataFrame['Date','Open','High','Low','Close','Volume'] | None
    '''
    if end_date is not None:
        try:
            data = client.get_historical_klines( symbol, interval, start_date, end_date ) 
        except BinanceAPIException as e:
            print(e)
            sleep(60)
            data = client.get_historical_klines( symbol, interval, start_date, end_date )    
    else:     
        try:
            data = client.get_historical_klines( symbol, interval, start_date ) 
        except BinanceAPIException as e:
            print(e)
            sleep(60)
            data = client.get_historical_klines( symbol, interval, start_date )   

    # convert result to DataFrame
    df = pd.DataFrame( data )
    # We fetched more data than we need, we just need the first six columns
    df = df.iloc[:,:6]
    # Now we will name our columns to the standard OHLCV
    df.columns = ['Date','Open','High','Low','Close','Volume']
    # Our index will be the UNIX timestamp, therefore we set datetime to index and make it more readable
    df = df.set_index('Date')        
    df.index = pd.to_datetime( df.index, unit='ms' )
    # We are handling mostly currencies so using float is necessary to calculate on the values later on
    df = df.astype(float)
    return df
