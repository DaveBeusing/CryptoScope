#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import ta



def confirmMomentum( df ):
    df[ 'RSI' ] = ta.momentum.rsi( df.Close, window=14, fillna=True )
    df[ 'MACD_Diff' ] = ta.trend.MACD( df.Close, window_fast=12, window_slow=26, window_sign=9, fillna=True ).macd_diff()
    df[ 'ATR' ] = ta.volatility.AverageTrueRange( high=df.High, low=df.Low, close=df.Close, window=14, fillna=True ).average_true_range()
    df[ 'OBV' ] = ta.volume.OnBalanceVolumeIndicator( close=df.Close, volume=df.Volume, fillna=True).on_balance_volume()
    df[ 'ROC' ] = ta.momentum.ROCIndicator( close=df.Close, window=3, fillna=True ).roc()
    return df

def applyIndicators( df ):
    ''' Apply Technical Indicators to given DataFrame

    We expect the following OHLCV columns within the given DataFrame
    ['Date','Open','High','Low','Close','Volume']

    Basic reading https://www.investopedia.com/terms/t/technical-analysis-of-stocks-and-trends.asp
    '''

    ## Momentum Indicators
    # https://www.investopedia.com/investing/momentum-and-relative-strength-index/
    ##

    '''
    Relative Strength Index (RSI)

    Compares the magnitude of recent gains and losses over a specified time period to measure speed and change of price movements of a security. 
    It is primarily used to attempt to identify overbought or oversold conditions in the trading of an asset.

    https://www.investopedia.com/terms/r/rsi.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.momentum.rsi
    '''
    df[ 'RSI' ] = ta.momentum.rsi( df.Close, window=14, fillna=True )


    '''
    Moving Average Convergence Divergence (MACD)

    Is a trend-following momentum indicator that shows the relationship between two moving averages of prices.
    The MACD is calculated by subtracting the 26-period exponential moving average (EMA) from the 12-period EMA.

    https://www.investopedia.com/terms/m/macd.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.MACD
    '''
    macd = ta.trend.MACD( df.Close, window_fast=12, window_slow=26, window_sign=9, fillna=True )
    df[ 'MACD' ] = macd.macd()
    df[ 'MACD_Diff' ] = macd.macd_diff() # MACD Histogram
    df[ 'MACD_Signal' ] = macd.macd_signal()


    '''
    Simple Moving Average (SMA)
    
    A simple moving average is an arithmetic moving average calculated by adding recent prices and then dividing that figure by the number of time periods in the calculation average. 
    For example, one could add the closing price of a security for a number of time periods and then divide this total by that same number of periods. 
    Short-term averages respond quickly to changes in the price of the underlying security, while long-term averages are slower to react.

    https://www.investopedia.com/terms/s/sma.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.sma_indicator
    '''
    # SMAs according to Binance
    df[ 'SMA7' ] = ta.trend.sma_indicator( df.Close, window=7, fillna=True )
    df[ 'SMA25' ] = ta.trend.sma_indicator( df.Close, window=25, fillna=True )
    df[ 'SMA60' ] = ta.trend.sma_indicator( df.Close, window=60, fillna=True )
    # Commonly used SMAs
    df[ 'SMA12' ] = ta.trend.sma_indicator( df.Close, window=12, fillna=True )
    df[ 'SMA26' ] = ta.trend.sma_indicator( df.Close, window=26, fillna=True )
    df[ 'SMA50' ] = ta.trend.sma_indicator( df.Close, window=50, fillna=True )
    df[ 'SMA200' ] = ta.trend.sma_indicator( df.Close, window=200, fillna=True )


    '''
    Parabolic Stop and Reverse (Parabolic SAR)

    The parabolic SAR is a widely used technical indicator to determine market direction, but at the same moment to draw attention to it once the market direction is changing. 
    This indicator also can be called the "stop and reversal system," the parabolic SAR was developed by J. Welles Wilder Junior. - the creator of the relative strength index (RSI).
    
    https://www.investopedia.com/terms/p/parabolicindicator.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.trend.PSARIndicator
    '''
    psar = ta.trend.PSARIndicator( high=df.High, low=df.Low, close=df.Close, step=0.02, max_step=2, fillna=True )
    df[ 'PSAR' ] = psar.psar()
    df[ 'PSAR_down' ] = psar.psar_down()
    df[ 'PSAR_down_ind' ] = psar.psar_down_indicator()
    df[ 'PSAR_up' ] = psar.psar_up()
    df[ 'PSAR_up_ind' ] = psar.psar_up_indicator()


    '''
    Bollinger Bands

    A Bollinger Band is a technical analysis tool outlined by a group of trend lines with calculated 2 standard deviations (positively and negatively) far from a straightforward moving average (SMA) of a market's value, 
    however which may be adjusted to user preferences. Bollinger Bands were developed and copyrighted by notable technical day trader John Bollinger and designed to get opportunities that could offer investors a better 
    likelihood of properly identifying market conditions (oversold or overbought). Bollinger Bands are a highly popular technique. Many traders believe the closer the prices move to the upper band, 
    the more overbought the market is, and the closer the prices move to the lower band, the more oversold the market is.

    https://www.investopedia.com/terms/b/bollingerbands.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.volatility.BollingerBands
    '''
    bb = ta.volatility.BollingerBands( close=df.Close, window=20, window_dev=2, fillna=True )
    df[ 'bb_avg' ] = bb.bollinger_mavg()
    df[ 'bb_high' ] = bb.bollinger_hband()
    df[ 'bb_low' ] = bb.bollinger_lband()


    '''
    Average True Range (ATR)
    
    The indicator provide an indication of the degree of price volatility. Strong moves, in either direction, are often accompanied by large ranges, or large True Ranges.

    The average true range (ATR) is a technical analysis indicator, introduced by market technician J. Welles Wilder Jr. in his book New Concepts in Technical Trading Systems, 
    that measures market volatility by decomposing the entire range of an asset price for that period.
    The true range indicator is taken as the greatest of the following: current high less the current low; the absolute value of the current high less the previous close; and the absolute value of the current low less the previous close. 
    The ATR is then a moving average, generally using 14 days, of the true ranges.

    https://www.investopedia.com/terms/a/atr.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.volatility.AverageTrueRange
    '''
    df[ 'ATR' ] = ta.volatility.AverageTrueRange( high=df.High, low=df.Low, close=df.Close, window=14, fillna=True ).average_true_range()


    '''
    On-balance volume (OBV)

    It relates price and volume in the stock market. OBV is based on a cumulative total volume.

    What is On-Balance Volume (OBV)?
    On-balance volume (OBV) is a technical trading momentum indicator that uses volume flow to predict changes in stock price. Joseph Granville first developed the OBV metric in the 1963 book Granville's New Key to Stock Market Profits.
    Granville believed that volume was the key force behind markets and designed OBV to project when major moves in the markets would occur based on volume changes. 
    In his book, he described the predictions generated by OBV as "a spring being wound tightly." 
    He believed that when volume increases sharply without a significant change in the stock's price, the price will eventually jump upward or fall downward.
    
    https://www.investopedia.com/terms/o/onbalancevolume.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.volume.OnBalanceVolumeIndicator
    '''
    df[ 'OBV' ] = ta.volume.OnBalanceVolumeIndicator( close=df.Close, volume=df.Volume, fillna=True).on_balance_volume()


    '''
    Rate of Change (ROC)

    The Rate-of-Change (ROC) indicator, which is also referred to as simply Momentum, is a pure momentum oscillator that measures the percent change in price from one period to the next. 
    The ROC calculation compares the current price with the price “n” periods ago. 
    The plot forms an oscillator that fluctuates above and below the zero line as the Rate-of-Change moves from positive to negative. 
    As a momentum oscillator, ROC signals include centerline crossovers, divergences and overbought-oversold readings. 
    Divergences fail to foreshadow reversals more often than not, so this article will forgo a detailed discussion on them. 
    Even though centerline crossovers are prone to whipsaw, especially short-term, these crossovers can be used to identify the overall trend. 
    Identifying overbought or oversold extremes comes naturally to the Rate-of-Change oscillator.

    https://www.investopedia.com/terms/p/pricerateofchange.asp
    https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html#ta.momentum.ROCIndicator
    '''
    df[ 'ROC' ] = ta.momentum.ROCIndicator( close=df.Close, window=3, fillna=True ).roc()



    '''
    return the augmented DataFrame
    '''
    return df
