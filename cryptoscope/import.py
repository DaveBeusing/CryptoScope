#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#
import json
from time import sleep
from os.path import isfile
from binance import Client, BinanceSocketManager
from cryptoscope import Config, Credentials, fetch_NonLeveragedTradePairs
credentials = Credentials( Config.Keyfile )
client = Client( credentials.key, credentials.secret )

'''
symbols = fetch_NonLeveragedTradePairs( client )
total_symbols = len(symbols)
current_symbol = 0
for symbol in symbols:
    current_symbol += 1    
    path = f'/home/dave/code/crypto/cs/database/meta/{symbol}.json'
    if isfile( path ):
        print( f'{current_symbol}/{total_symbols} {symbol} (ok)\n')
    else:
        print( f'{current_symbol}/{total_symbols} {symbol} (fetch)\n')
        meta = client.get_symbol_info( symbol )
        with open( path, 'w+' ) as file:
            file.write( json.dumps( meta ) )
        #APIError(code=-1003): Too much request weight used; current limit is 1200 request weight per 1 MINUTE. Please use the websocket for live updates to avoid polling the API.
        #to avoid the before mentioned error we will sleep 1sec after each fetched symbol
        sleep(1) 
'''


path = f'/home/dave/code/crypto/cs/database/meta/LRCUSDT.json'
if isfile( path ):
    with open( path, 'r' ) as file:
        meta = json.loads( file.read() )
        #print(meta)

print( meta['quoteAsset'] )