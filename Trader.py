#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import asyncio
import pandas as pd
from datetime import datetime
from binance import Client, BinanceSocketManager
from cryptoscope import Config, Credentials, IPC, Database, build_Frame, log
from cryptoscope import Asset, Order, Trade

credentials = Credentials( Config.Keyfile )
client = Client( credentials.key, credentials.secret )
client.timestamp_offset = -2000 #binance.exceptions.BinanceAPIException: APIError(code=-1021): Timestamp for this request was 1000ms ahead of the server's time.
db = Database()

if not IPC.get( IPC.isRunning ):

    print( f'{str(datetime.now())} Start Trader' )

    TradePairs = db.fetchTopPerformer( lookback=2, maximum=5 )
    '''
        In der Regel geht das ZWEIT platzierte Symbol hoch, ergo da liegt das meiste potential
        Das momentum des ERST platzierten is ggf. nicht mehr gegeben oder deutlich schwächer als des ZWEIT platzierten
    '''
    asset = Asset( client, TradePairs[1]['symbol'], OHLCV=True, Indicators=True )
    '''
        Hier sollte nochmal geprüft werden ob das momentum noch gegeben ist und ggf. auf TradePairs[2] ... etc. gewechselt werden.
        Siehe /home/dave/code/crypto/bot/CryptoTrader.py
    '''

    # Recheck if bot is not yet running already
    if not IPC.get( IPC.isRunning ):
        # We want to place our trade now so set IPC.isRunning as quick as possible
        price = db.getRecentPrice( asset.symbol ) #db vs asset db spart 1x HTTP query / asset ggf. mehr akkurat

        #APIError(code=-1111): Precision is over the maximum defined for this asset.
        #RLCUSDT BUY 19.900000000000002 5.008
        #quantity = asset.calculateQTY( Config.Investment, price=price )
        quantity = asset.tradeVolume( Config.Investment, price=price )

        if Config.isPaperTrade is not None:
            order = Order( client, asset, Order.BUY, quantity, price, isPaperTrade=True )
        else:    
            order = Order( client, asset, Order.BUY, quantity, price )

        entry_slippage = round( (order.price - price) / price *100, 2 )
        print( f'{str(datetime.now())} Order {asset.symbol} QTY:{order.qty} ASK:{order.price} ({price}/{entry_slippage}%)' )
        
        #TODO: implement logging
    else:    
        # IPC.isRunning
        print( f'{str(datetime.now())} Found an opportunity, but we are already invested.' )
        quit()
        pass

else:
    # IPC.isRunning
    print( f'{str(datetime.now())} We are already invested.' )
    quit()


#################################
### Monitor the current trade ###
#################################
async def main( asset, BuyOrder ):
    bsm = BinanceSocketManager( client )
    ts = bsm.trade_socket( asset.symbol )
    print( f'{str(datetime.now())} Start monitor {asset.symbol}' )
    async with ts as tscm:
        while True:
            response = await tscm.recv()
            if response:
                
                frame = build_Frame( response )
                CurrentPrice = frame.Price.iloc[-1]

                #TODO: wir testen eine price history um die volatilität sowie low & high zu berechnen
                BuyOrder.history.append( { 'Date': str(datetime.now()), 'Price' : float(CurrentPrice) })

                TakeProfit = float( BuyOrder.price ) + ( float( BuyOrder.price ) * float( Config.TakeProfit ) ) / 100
                StopLoss = float( BuyOrder.price ) + ( float( BuyOrder.price ) * float( -Config.StopLoss ) ) / 100
                #BreakEven = float( BuyOrder.price ) + ( float( BuyOrder.price ) * float( Config.BreakEven ) ) / 100

                print( f'{str(datetime.now())} {asset.symbol} BP:{BuyOrder.price} CP:{CurrentPrice} TP:{TakeProfit} SL:{StopLoss} ' )

                # Exit Trade
                if CurrentPrice < StopLoss or CurrentPrice > TakeProfit:
                    # We are exiting this trade, so free the IPC Signal as quick as possible to let the Bot start a new trade
                    IPC.set( IPC.isRunning, delete=True )

                    # binance.exceptions.BinanceAPIException: APIError(code=-2010): Account has insufficient balance for requested action
                    # If we buy an asset we pay fee's with the bought asset, therefore we need to deduct the fee amount before we try to sell the position
                    # If we sell an asset the fee will be calculated (in our case) in USDT
                    #SellQTY = float( BuyOrder.qty - BuyOrder.commission )
                    SellQTY = asset.formatLotSize( float( BuyOrder.qty - BuyOrder.commission ) ) 
                    

                    # binance.exceptions.BinanceAPIException: APIError(code=-1013): Filter failure: LOT_SIZE
                    # read this post by Sam McHardy -> https://sammchardy.github.io/binance-order-filters/

                    if Config.isPaperTrade is not None:
                        SellOrder = Order( client, asset, Order.SELL, SellQTY, CurrentPrice, isPaperTrade=True )
                    else:
                        SellOrder = Order( client, asset, Order.SELL, SellQTY, CurrentPrice )                        

                    # APIError(code=-2010): Account has insufficient balance for requested action.
                    # UNFIUSDT SELL 8.3 12.067

                    class Meta:
                        Investment = Config.Investment
                        TakeProfit = Config.TakeProfit
                        StopLoss = Config.StopLoss
                        BreakEven = Config.BreakEven
                        TradingFee = Config.TradingFee
 
                    trade = Trade( BuyOrder, SellOrder, asset, Meta )
                    trade.printReport()


                    ### Reporting START ###

                    ask_costs = float( BuyOrder.price * BuyOrder.qty )
                    bid_costs = float( (SellOrder.price * SellOrder.qty) - SellOrder.commission )


                    Dust = float( BuyOrder.qty - SellOrder.qty )
                    ProfitPerShare = float( SellOrder.price - BuyOrder.price ) 
                    ProfitTotal = float( ProfitPerShare * SellOrder.qty ) 
                    ProfitRelative = float( ( SellOrder.price - BuyOrder.price ) / BuyOrder.price ) 
                    Diff = round(( SellOrder.price - BuyOrder.price ) / BuyOrder.price *100, 2 )
                    #p = P / G
                    Duration = str( datetime.now() - datetime.fromtimestamp( BuyOrder.timestamp ) )
                    state = None
                    if SellOrder.price > BuyOrder.price:
                        state = 'WON'
                    else:
                        state = 'LOST' 
                    ds = { 'ts' : str(datetime.now()), 'state' : state, 'symbol' : asset.symbol, 'duration' : str(Duration), 'ask' : str(BuyOrder.price), 'ask_qty' : str(BuyOrder.qty), 'bid' : str(SellOrder.price), 'bid_qty' : str(SellOrder.qty), 'profit' : str(ProfitPerShare), 'total_profit' : str(ProfitTotal), 'ROC' : asset.OHLCV.ROC.iloc[-1], 'RSI' : asset.OHLCV.RSI.iloc[-1], 'ATR' : asset.OHLCV.ATR.iloc[-1], 'OBV' : asset.OHLCV.OBV.iloc[-1] }
                    log( ds, timestamp=False )
                   

                    #Stop & Exit the Loop
                    loop.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    '''
    Traceback (most recent call last):
    File "/home/dave/code/crypto/bot/CryptoPro.py", line 173, in <module>
    loop.run_until_complete( main( asset, order ) )
    File "/usr/lib/python3.9/asyncio/base_events.py", line 640, in run_until_complete
    raise RuntimeError('Event loop stopped before Future completed.')
    RuntimeError: Event loop stopped before Future completed.
    '''
    try:
        loop.run_until_complete( main( asset, order ) )
    except RuntimeError as e:
        if e == 'Event loop stopped before Future completed.':
            pass
