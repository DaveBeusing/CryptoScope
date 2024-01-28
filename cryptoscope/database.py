#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from cryptoscope import Config


class Database:

    def __init__( self ):
        self.engine = create_engine( f'sqlite:///{Config.Database}' )


    def getRecentPrice( self, symbol ):
        #query = f"SELECT Close FROM '{symbol}' DESC LIMIT 1"
        query = f"SELECT Date, Close FROM '{symbol}' ORDER BY Date DESC LIMIT 1"
        data = pd.read_sql( query, self.engine )
        return data.Close.iloc[-1]


    def fetchSymbols( self ):
        symbols = pd.read_sql( 'SELECT name FROM sqlite_master WHERE type = "table"', self.engine ).name.to_list()
        return symbols


    def fetchTopPerformer( self, lookback:int=2, maximum:int=0 ):
        ''' fetches Top performing Symbols by calculating cumulative return

        :param:int:lookback -> Lookback period in minutes
        :param:int:maximum -> Maximum returned symbols
        '''
        symbols = self.fetchSymbols()
        returns = []
        for symbol in symbols:
            prices = self.fetchSymbol( symbol, lookback ).Close #last 2 minutes .Price
            cumulative_return = float( ( prices.pct_change() + 1 ).prod() - 1 )
            cumulative_return = float( f'{cumulative_return:.8f}' )
            if cumulative_return > 0.0:
                returns.append( { 'symbol' : symbol, 'cumret' : cumulative_return } )

        # sort descending
        sorted_returns = sorted( returns, key=lambda d: d['cumret'], reverse=True )

        if maximum > 0:
            return sorted_returns[:maximum]
        else:
            return sorted_returns


    def fetchSymbol( self, symbol, lookback:int, delta=1 ):
        ''' fetch Symbol data

        :param:str:symbol       Symbol
        :param:int:lookback     Lookback period in minutes
        :param:int:delta        Timedelta in hours between local and binance server time
        '''
        lookback = lookback * 60
        now = datetime.now() - timedelta( hours=delta )
        before = now - timedelta( seconds=lookback)
        #query = f"SELECT * FROM '{symbol}' WHERE isClosed=1 AND DATE >= '{before}'"
        query = f"SELECT * FROM '{symbol}' WHERE DATE >= '{before}'"
        return pd.read_sql( query, self.engine )
    

    def fetchSymbolOHLCV( self, symbol ):
        query = f"SELECT Date, Symbol, Open, High, Low, Close, Volume FROM '{symbol}' WHERE isClosed=1"
        return pd.read_sql( query, self.engine )
        
        

