#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import pandas as pd

def build_Frame( msg, isMultiStream=None, isOHLCV=None, isImport=None ):
    
    if isMultiStream is not None:
        if isOHLCV is not None:
            msg[ 'data' ]['k']['E'] = msg['data']['E']
            df = pd.DataFrame( [ msg[ 'data' ]['k'] ] )
        else:
            df = pd.DataFrame( [ msg[ 'data' ] ] )
    else:       
        df = pd.DataFrame( [msg] )

    if isOHLCV is not None:
        '''
        https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
        Attention !! -> data.E moved into data.k.E
        {
            'stream': 'btcusdt@kline_1m',           // Stream type
            'data': {                               
                'e': 'kline',                       // Event type
                'E': 1638137674135,                 // Event time
                's': 'BTCUSDT',                     // Symbol
                'k': {
                    't': 1638137640000,             // Kline start time
                    'T': 1638137699999,             // Kline close time
                    's': 'BTCUSDT',                 // Symbol
                    'i': '1m',                      // Interval
                    'f': 1166557616,                // First trade ID
                    'L': 1166558366,                // Last trade ID
                    'o': '56510.44000000',          // Open price
                    'c': '56575.17000000',          // Close price
                    'h': '56583.87000000',          // High price
                    'l': '56483.46000000',          // Low price
                    'v': '26.85358000',             // Base asset volume
                    'n': 751,                       // Number of trades
                    'x': False,                     // Is this kline closed?
                    'q': '1517957.80173370',        // Quote asset volume
                    'V': '18.72274000',             // Taker buy base asset volume
                    'Q': '1058294.04643240',        // Taker buy quote asset volume
                    'B': '0'                        // Ignore (Unknown/not public)
                }
            }
        }
        '''
        if isImport is not None:
            df = df.loc[ :, [ 'E', 's', 'o', 'h', 'l', 'c', 'v', 'x' ] ] 
            df.columns = [ 'Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'isClosed' ]
            df.isClosed = df.isClosed.astype( bool )
        else:
            df = df.loc[ :, [ 'E', 's', 'o', 'h', 'l', 'c', 'v' ] ] 
            df.columns = [ 'Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume' ]
                
        df.Open = df.Open.astype( float )
        df.High = df.High.astype( float )
        df.Low = df.Low.astype( float )
        df.Close = df.Close.astype( float )
        df.Volume = df.Volume.astype( float )
    else:
        '''
        https://binance-docs.github.io/apidocs/spot/en/#trade-streams
            {
                'stream': 'btcusdt@trade',          // Stream type
                'data': {
                    'e': 'trade',                   // Event type
                    'E': 1637081506351,             // Event time
                    's': 'BTCUSDT',                 // Symbol
                    't': 1148079548,                // Trade ID
                    'p': '60646.40000000',          // Price
                    'q': '0.00031000',              // Quantity
                    'b': 8283146847,                // Buyer order ID
                    'a': 8283146313,                // Seller order ID
                    'T': 1637081506349,             // Trade time
                    'm': False,                     // Is the buyer the market maker?
                    'M': True                       // Ignore
                }
            }
        '''       
        df = df.loc[ :, [ 'E', 's', 'p' ] ] 
        df.columns = [ 'Date', 'Symbol', 'Price' ]
        df.Price = df.Price.astype( float )

  
    df.Date = pd.to_datetime( df.Date, unit='ms' )
    return df
