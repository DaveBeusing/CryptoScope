#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import math
from math import floor
from json import dumps, loads
from os.path import isfile
from cryptoscope import Config, Database
from cryptoscope import fetch_OHLCV
from cryptoscope import applyIndicators
from cryptoscope.indicators import confirmMomentum

class Asset:

    def __init__( self, client, symbol, OHLCV=None, Indicators=None ):
        
        self.MetaCache = Config.MetaCache
        self.binance = client
        self.symbol = symbol
        self.db = Database()
        self.OHLCV = None

        self.fetchMetadata()

        if OHLCV is not None:
            self.fetchOHLCV()

        if OHLCV and Indicators is not None:
            self.applyOHLCVindicators()


    def tradeVolume( self, amount, price=None ):
        #https://github.com/CyberPunkMetalHead/Binance-volatility-trading-bot/blob/533daf54c0c47390d2d51daa67fec8127da4a829/Binance%20Detect%20Moonings.py#L252

        if price == None:
            price = self.getRecentPrice()    

        volume = float( amount / float( price ) )
        if self.lotSize == 0:
            volume = int( volume )
        else:
            volume = float( '{:.{}f}'.format( volume, self.lotSize ) )
        
        return volume

    def formatLotSize( self, qty ):
        if self.lotSize == 0:
            qty = int( qty )
        else:
            #qty = float( '{:.{}f}'.format( qty, self.lotSize ) )
            qty = self._round_down( qty, decimals=self.lotSize )
        return qty

    def formatPrecision( self, num, precision ):
        return float( '{:.{}f}'.format( num, precision ) )

    def _round_down( self, n, decimals=0 ):
        #https://realpython.com/python-rounding/
        multiplier = 10 ** decimals
        return floor(n * multiplier) / multiplier


    def fetchOHLCV(self):
        #self.OHLCV = fetch_OHLCV( self.binance, self.symbol, interval='1m', start_date='60 minutes ago UTC' )
        self.OHLCV = self.db.fetchSymbolOHLCV( self.symbol )


    def applyOHLCVindicators(self):
        #pass
        #applyIndicators( self.OHLCV )
        confirmMomentum( self.OHLCV )


    def calculateQTY( self, amount, price=None ):
        if price is not None:
            price = price
        else:
            price = self.getRecentPrice()
        return float( floor( float( amount ) / ( float( price ) * self.minQTY ) ) *  self.minQTY  )


    def getRecentPrice( self ):

        #price = self.db.getRecentPrice( self.symbol )

        #TODO catch Exceptions
        return float( self.binance.get_symbol_ticker( symbol=self.symbol )['price'] )


    def _localMetadata( self ):
        if isfile( f'{self.MetaCache}{self.symbol}.json' ):
            with open( f'{self.MetaCache}{self.symbol}.json', 'r' ) as file:
                meta = loads( file.read() )
        else:
            meta = self._remoteMetadata()
        return meta


    def _remoteMetadata( self):
        meta = self.binance.get_symbol_info( self.symbol )
        with open( f'{self.MetaCache}{self.symbol}.json', 'w+' ) as file:
            file.write( dumps( meta, indent=2 ) )
        return meta


    def fetchMetadata( self ):
        #https://sammchardy.github.io/binance-order-filters/

        meta = self._localMetadata()

        self.base = meta['baseAsset']
        self.basePrecision = int( meta['baseAssetPrecision'] )
        self.quote = meta['quoteAsset']
        self.quotePrecision = int( meta['quoteAssetPrecision'] )
        self.isSpot = meta['isSpotTradingAllowed']
        self.isMargin = meta['isMarginTradingAllowed']
        self.minQTY = float( meta['filters'][2]['minQty'] )
        self.maxQTY = float( meta['filters'][2]['maxQty'] )
        #self.stepSize = float( meta['filters'][2]['stepSize'] )
        self.stepSize = meta['filters'][2]['stepSize']
        self.tickSize = float( meta['filters'][0]['tickSize'] )
        self.minNotional = float( meta['filters'][3]['minNotional'] )

        #https://github.com/CyberPunkMetalHead/Binance-volatility-trading-bot/blob/533daf54c0c47390d2d51daa67fec8127da4a829/Binance%20Detect%20Moonings.py#L252
        self.lotSize = self.stepSize.index('1') - 1
        if self.lotSize < 0:
            self.lotSize = 0

        self.lotSize = int(self.lotSize)

        '''
        {'symbol': 'LRCUSDT',
        'status': 'TRADING',
        'baseAsset': 'LRC',
        'baseAssetPrecision': 8,
        'quoteAsset': 'USDT',
        'quotePrecision': 8,
        'quoteAssetPrecision': 8,
        'baseCommissionPrecision': 8,
        'quoteCommissionPrecision': 8,
        'orderTypes': [
            'LIMIT',
            'LIMIT_MAKER',
            'MARKET',
            'STOP_LOSS_LIMIT',
            'TAKE_PROFIT_LIMIT'
        ],
        'icebergAllowed': True,
        'ocoAllowed': True,
        'quoteOrderQtyMarketAllowed': True,
        'isSpotTradingAllowed': True,
        'isMarginTradingAllowed': True,
        'filters': [
         {'filterType': 'PRICE_FILTER',
          'minPrice': '0.00010000',
          'maxPrice': '1000.00000000',
          'tickSize': '0.00010000'},
         {'filterType': 'PERCENT_PRICE',
          'multiplierUp': '5',
          'multiplierDown': '0.2',
          'avgPriceMins': 5},
         {'filterType': 'LOT_SIZE',
          'minQty': '1.00000000',
          'maxQty': '9000000.00000000',
          'stepSize': '1.00000000'},
         {'filterType': 'MIN_NOTIONAL',
          'minNotional': '10.00000000',
          'applyToMarket': True,
          'avgPriceMins': 5},
         {'filterType': 'ICEBERG_PARTS', 'limit': 10},
         {'filterType': 'MARKET_LOT_SIZE',
          'minQty': '0.00000000',
          'maxQty': '448756.44475330',
          'stepSize': '0.00000000'},
         {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200},
         {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}],
        'permissions': ['SPOT', 'MARGIN']}
        '''