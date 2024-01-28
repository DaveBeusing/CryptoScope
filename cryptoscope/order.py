#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import numpy as np
from time import sleep
from datetime import datetime
from cryptoscope import Config, log
from binance.exceptions import BinanceAPIException

class Order:

    BUY = 'BUY'
    SELL = 'SELL'

    def __init__( self, client, asset, side, quantity, price, isPaperTrade=None ):

        self.binance = client
        self.asset = asset
        self.symbol = asset.symbol
        self.side = side
        self.qty = quantity
        self.bid = float(price)
        
        #############
        ### Order ###
        #############
        if isPaperTrade is not None:
            self.order = self.paperTrade( self.side, self.symbol, self.qty, self.bid, self.asset.basePrecision )
        else:
            try:
                self.order = self.binance.create_order( symbol=self.symbol, side=self.side, type='MARKET', quantity=self.qty )                
                with open( Config.BinanceLogfile, 'a+' ) as fd:
                    fd.write( f'{str(datetime.now())} {self.order}\n' )
      
            except BinanceAPIException as e:
                print( f'{e} \n{self.symbol} {self.side} {self.qty} {self.bid}' )
        
        # APIError(code=-1013): Filter failure: LOT_SIZE
        # TCTUSDT SELL 445.554 0.04888        

        # APIError(code=-2010): Account has insufficient balance for requested action.
        # UNFIUSDT SELL 8.3 12.067
        # SellQTY > CurrentQTY (Fee's müssen berücksichtigt werden)

        # APIError(code=-1111): Precision is over the maximum defined for this asset.
        # MASKUSDT BUY 0.6000000000000001 16.604
        # RLCUSDT BUY 19.900000000000002 5.008

        # APIError(code=-1013): Filter failure: MIN_NOTIONAL
        # RNDRUSDT BUY 1.74 5.719


        
        self.qty = float( self.order['executedQty'] )
        self.price = sum( [ float( f['price'] ) * ( float( f['qty'] ) / float( self.qty ) ) for f in self.order['fills'] ] )
        self.commission = sum( [ float( f['commission'] ) for f in self.order['fills'] ] )
        self.slippage = float( self.price - self.bid )
        self.id = self.order['orderId']
        self.timestamp = datetime.now().timestamp()

        self.history = []

        self.TP = None
        self.TTP = None
        self.SL = None
        self.TSL = None

    def stringify(self):
        return {
            'symbol' : self.symbol,
            'side' : self.side,
            'qty' : self.qty,
            'bid' : self.bid,
            'price' : self.price,
            'commission' : self.commission,
            'slippage' : self.slippage,
            'timestamp' : str(self.timestamp),
            'TP' : self.TP,
            'TTP' : self.TTP,
            'SL' : self.SL,
            'TSL' : self.TSL,
            'order' : self.order
        }

    def trail( self, mode, type, value=None ):
        ''' Basic get/set of Traling TakeProfit/StopLoss

        :param mode:str:    -> get|set
        :param type:str:    -> TTP|TSL
        :param value:float: -> value to sets
        '''        
        if type == 'TTP':
            if mode == 'set':
                self.TTP = value
            return self.TTP
        if type == 'TSL':
            if mode == 'set':
                self.TSL = value
            return self.TSL



    def paperTrade( self, side, symbol, qty, price, precision ):
        # artificial delay
        sleep(1)

        #'origQty': '12.30000000' '0.00020000' '0.01210000'
        origQTY = qty
        quoteQTY = float( qty*price )
        halfedQTY = float( origQTY/2 )
        batch1QTY = float( halfedQTY + (halfedQTY/2) )
        batch1Fee = float( round( ( batch1QTY / 100 ) * float(0.1), precision ) )
        batch2QTY = float( halfedQTY/2 )
        batch2Fee = float( round( ( batch2QTY / 100 ) * float(0.1), precision ) )

        order = {
            'symbol': symbol, 
            'orderId': 22107854, 
            'orderListId': -1, 
            'clientOrderId': 'DkGnomuTY9lz4kkALHQ87f', 
            'transactTime': 1637194823283, 
            'price': '0.00000000', 
            'origQty': origQTY, 
            'executedQty': origQTY, 
            'cummulativeQuoteQty': quoteQTY, 
            'status': 'FILLED', 
            'timeInForce': 'GTC', 
            'type': 'MARKET', 
            'side': side, 
            'fills': [
                {
                'price': price, 
                'qty': batch1QTY, 
                'commission': batch1Fee, 
                'commissionAsset': symbol, 
                'tradeId': 2498963
                }, 
                {
                'price': price, 
                'qty': batch2QTY, 
                'commission': batch2Fee, 
                'commissionAsset': symbol, 
                'tradeId': 2498964
                }
            ]
        }

        return order