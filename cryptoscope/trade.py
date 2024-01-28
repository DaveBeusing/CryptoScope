#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import pandas as pd
from datetime import datetime

class Trade:
    #https://www.investopedia.com/terms/b/bid-and-ask.asp
    def __init__( self, ask, bid, asset, meta ):
        '''
        :param:Order object:ask - Object of the buy (ask/long) order
        :param:Order object:bid - Object of the sell (bid/short) order
        '''
        self.ask = ask
        self.bid = bid
        self.asset = asset
        self.meta = meta

        self.isPaperTrade = True
        self.logPath = '/home/dave/code/crypto/cs/log/tradelog.log'

        # create the trade object
        self._prepare()

    def formatPrecision( self, num, precision ):
        return float( '{:.{}f}'.format( num, precision ) )

    def _prepare( self ):
        '''
            zusammenfassen beider order parts und auswertung
        '''
        df = pd.DataFrame( self.ask.history )
        df.columns = [ 'Date', 'Price' ]
        df.Price.astype(float)
        min = df.Price.min()
        max = df.Price.max()        
        trade_spread = round( ( max - min ) / max * 100, 2 )
        ask_costs = float( self.ask.price * self.ask.qty )
        bid_costs = float( (self.bid.price * self.bid.qty) - self.bid.commission )
        PnL = self.formatPrecision( float( bid_costs - ask_costs ), 4 )
        relPnL = round( float( (bid_costs - ask_costs) / ask_costs * 100 ), 2 )

        state = 'LOST'
        if self.bid.price > self.ask.price:
            state = 'WON'
        
        mode = 'PaperTrade'
        if self.isPaperTrade == False:
            mode = 'MarketTrade'
        
        self.timestamp = str( datetime.now() )
        self.Symbol = self.ask.symbol
        self.Mode = mode
        self.State = state
        self.SeedInvest = self.meta.Investment
        self.Investment = self.formatPrecision( ask_costs, 4 )
        self.Return = self.formatPrecision( bid_costs, 4 )
        self.PnL = PnL
        self.relPnL = relPnL
        self.TradeSpread = trade_spread
        self.Drawdown = round( ( self.ask.price - min ) / self.ask.price * 100, 2 )
        self.TradeMinPrice = min
        self.TradeMaxPrice = max
        self.TakeProfit = self.meta.TakeProfit
        self.StopLoss = self.meta.StopLoss
        self.BreakEven = self.meta.BreakEven
        self.TradingFee = self.meta.TradingFee
        self.Duration = str( datetime.fromtimestamp( self.bid.timestamp ) - datetime.fromtimestamp( self.ask.timestamp ) )
        self.Dust = self.formatPrecision( ( self.ask.qty - self.ask.commission ) - self.bid.qty, self.asset.basePrecision )  
        self.ask_date = datetime.fromtimestamp( self.ask.timestamp )
        self.ask_price = self.ask.price
        self.ask_qty = self.ask.qty
        self.ask_fee = self.ask.commission
        self.ask_slippage = self.ask.slippage        
        self.bid_date = datetime.fromtimestamp( self.bid.timestamp )
        self.bid_price = self.bid.price
        self.bid_qty = self.bid.qty
        self.bid_fee = self.bid.commission
        self.bid_slippage = self.bid.slippage
        self.asset_ROC = self.asset.OHLCV.ROC.iloc[-1]
        self.asset_RSI = self.asset.OHLCV.RSI.iloc[-1]
        self.asset_ATR = self.asset.OHLCV.ATR.iloc[-1]
        self.asset_OBV = self.asset.OHLCV.OBV.iloc[-1]
        self.ask = self.ask.stringify()
        self.bid = self.bid.stringify()

        # write trade object to logfile
        #self._write_tradelog()


    def _write_tradelog( self ):
        with open( self.logPath, 'a+' ) as fd:
            fd.write( f'{self.trade}\n' )
    
    def printReport( self ):
        print( f'###_Report_###' )
        print( f'Date : {self.timestamp}' )
        print( f'Symbol : {self.Symbol}' )
        print( f'Mode : {self.Mode}' )
        print( f'Condition : {self.State}' )
        print( f'Opened : {self.ask_date}' )
        print( f'Closed : {self.bid_date}' )
        print( f'Duration : {self.Duration}' )
        print( f'Seed Invest : {self.SeedInvest} USDT' )
        print( f'Investment : {self.Investment} USDT' )
        print( f'Return : {self.Return} USDT' )
        print( f'PnL : {self.PnL} USDT' )
        print( f'PnL : {self.relPnL} %' )
        print( f'Trade Spread : {self.TradeSpread} %' )
        print( f'Drawdown : {self.Drawdown} %' )
        print( f'TakeProfit : {self.TakeProfit} %' )
        print( f'BreakEven : {self.BreakEven} %' )
        print( f'StopLoss : {self.StopLoss} %' )
        print( f'Fee : {self.TradingFee} %' )        
        print( f'Dust : {self.Dust}' )
        print( f'ROC : {self.asset_ROC}' )
        print( f'RSI : {self.asset_RSI}' )
        print( f'ATR : {self.asset_ATR}' )
        print( f'OBV : {self.asset_OBV}' )
        print( f'##############' )
