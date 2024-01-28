
import json
from binance import Client, BinanceSocketManager
from cryptoscope import Config, Database
from cryptoscope import Asset
from cryptoscope import Credentials
import matplotlib.pyplot as plt



credentials = Credentials( 'key/binance.key' ) # alternative -> key/testnet.key
client = Client( credentials.key, credentials.secret ) 
client.timestamp_offset = -2000 #binance.exceptions.BinanceAPIException: APIError(code=-1021): Timestamp for this request was 1000ms ahead of the server's time.
db = Database()


#
#meta = client.get_symbol_info('BEAMUSDT')
#print( json.dumps( meta, indent=2 ) )
#



#asset = Asset( client, 'TCTUSDT' )
#print( asset.tradeVolume(100) )
#print( asset.calculateQTY(100) )


#TradePairs = db.fetchTopPerformer( lookback=2, maximum=5 )


import ast
import pandas as pd
data = []
with open( '/home/dave/code/crypto/cs/log/cumret.log' ) as fd:
    lines = fd.readlines()
for line in lines:
    line = ast.literal_eval( line.rstrip() )
    ds = { 'date' : line['date'], 'query' : line['query'] }
    cnt=0
    for entry in line['data']:
        cnt += 1
        ds[ f'symbol{cnt}' ] = entry['symbol']
        ds[ f'cumret{cnt}' ] = entry['cumret']

    data.append(ds)
    #data.append( ast.literal_eval( line.rstrip() ) )
fd.close()

df = pd.DataFrame( data )