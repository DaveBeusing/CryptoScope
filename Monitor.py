#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

from timeit import default_timer
from time import sleep
from os import system
from datetime import datetime
from cryptoscope import Config, Credentials
from cryptoscope import Database

from binance import Client, AsyncClient, BinanceSocketManager


credentials = Credentials( Config.Keyfile )
client = Client( credentials.key, credentials.secret )
db = Database()

clear = lambda: system( 'clear' )




while True:

    start = default_timer()
    TradePairs = db.fetchTopPerformer( lookback=2, maximum=5 )
    stop = default_timer()
    duration = round(stop - start, 4)
     
    data = { 'date' : str( datetime.now() ), 'query' : duration, 'data' : TradePairs  }

    with open( 'log/cumret.log', 'a+' ) as fd:
        fd.write( f'{data}\n' )

    print( f'\nQuery: {duration} seconds')
    for entry in TradePairs:
        print( f"{entry['symbol']} {entry['cumret']}" )

    #sleep(5)
    #clear()