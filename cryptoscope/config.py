#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#


class Config:

    # If you're brave enough do real orders :)
    isPaperTrade = True # None or True

    Keyfile = 'key/binance.key'
    Logfile = 'log/logfile.log'
    Database = 'database/CryptoScope.db'
    MetaCache = 'database/meta/'
    BinanceLogfile = 'log/binance.log'

    # Total amount per trade in USDT
    # Binance uses a minimum of 10 USDT per trade, add a bit extra to enable selling if the price drops.
    # Recommended: no less than 12 USDT. Suggested: 15 or more.
    Investment = 100 

    # define in % when to take profit.
    # when hit TakeProfit move TakeProfit up by TrailingTakeProfit %
    TakeProfit = 0.8 #0.4
    TrailingTakeProfit = 0.1

    # define in % when break even is reached (0.2% fee)
    BreakEven = 0.2

    # define in % when to sell a coin that's not making a profit.
    # when hit TakeProfit move StopLoss to TrailingStopLoss % below TakeProfit hence looking in profit
    StopLoss = 0.4
    TrailingStopLoss = 0.4
    
    # Trading Fee (commission) in % per trade
    # Binance standard is 0.1%, can be lowered to 0.075% by using BNB    
    TradingFee = 0.1
    # If using BNB for fees, it MUST be enabled in your Binance 'Dashboard' page (checkbox).
    isBNB = False