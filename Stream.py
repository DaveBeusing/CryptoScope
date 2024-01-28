#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
# CryptoScope Stream Engine

import asyncio

from os import remove, stat, system, getpid
from os.path import exists
from datetime import datetime

from cryptoscope import Config, Credentials
from cryptoscope import fetch_NonLeveragedTradePairs, build_Frame

from binance import Client, AsyncClient, BinanceSocketManager
from sqlalchemy import create_engine

credentials = Credentials( Config.Keyfile )
client = Client( credentials.key, credentials.secret )


clear = lambda: system( 'clear' )
def convert_bytes(size):
    #https://stackoverflow.com/a/59174649
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

    return size

pid = getpid()
StartTime = datetime.now()
print( f'{str(datetime.now())} OHLCV Stream started')

# Cleanup old data
if exists( Config.Database ):
    remove( Config.Database )

engine = create_engine( f'sqlite:///{Config.Database}' )
TradePairs = fetch_NonLeveragedTradePairs( client, streamFormat='@kline_1m' )

async def main():
    asyncClient = await AsyncClient.create()
    bsm = BinanceSocketManager( asyncClient )
    ms = bsm.multiplex_socket( TradePairs )
    cnt = 0
    async with ms as tscm:
        while True:
            response = await tscm.recv()
            if response:
                frame = build_Frame( response, isMultiStream=True, isOHLCV=True, isImport=True )
                frame.to_sql( frame.Symbol[0], engine, if_exists='append', index=False )
            
            cnt += 1
            if cnt == 10000:
                cnt = 0
                clear()
                db_size = convert_bytes( stat(Config.Database).st_size )
                runtime = datetime.now() - StartTime
                print( f'{str(datetime.now())} \n\n OHLCV stream running (PID:{pid})\n Runtime: {runtime}\n Database size {db_size}' )

    await asyncClient.close_connection()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete( main() )