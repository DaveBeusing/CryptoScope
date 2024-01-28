

--SELECT Date, Close FROM BTCUSDT GROUP BY strftime('%M', Date)
--SELECT Date, Close FROM BTCUSDT WHERE isClosed = 1

-SELECT Date, Symbol, Open, High, Low, Close, Volume, isClosed FROM CTXCUSDT DESC

--SELECT Date, Symbol, Open, High, Low, Close, Volume, isClosed FROM CTXCUSDT DESC

--SELECT Date, Close FROM CTXCUSDT ASC LIMIT 1

--SELECT Date, Close FROM CTXCUSDT ORDER BY Date DESC LIMIT 1

SELECT Date, Symbol, Close FROM TROYUSDT ORDER BY Date DESC LIMIT 1
SELECT Date, Close FROM TROYUSDT ORDER BY Date DESC LIMIT 1

SELECT sql FROM sqlite_schema WHERE name = 'TROYUSDT';
