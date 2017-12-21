import sqlite3
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
import sys

global inserts
inserts = []
def create_inserts(symbol):
    try:
        symbol = symbol.strip()
        path = 'data/dailies/daily_'+symbol+'.csv'
        symbol_data = pd.read_csv(path, usecols=['timestamp', 'close'])
        for idx, row in symbol_data.iterrows():
            date_string, close = row['timestamp'], row['close']
            inserts.append('INSERT INTO CLOSE (SYMBOL, DAY, CLOSE) ' + \
                       'VALUES ("' + symbol + '", "' + date_string + '",' + str(close) + ')')
        return True
    except OSError as e:
        print(symbol)
        print(e)
        return False
    except IndexError as ie:
        print(symbol)
        print(ie)
        return False


db = sqlite3.connect('beta_schema.db')
pool = ThreadPool(50)
symbols = list(pd.read_csv('data/market_symbols.csv', header=None)[0])

results = pool.map(create_inserts, symbols)

while len(inserts) > 0:
    db.execute(inserts.pop())

db.commit()
db.close()
pool.close()
pool.join()

sys.exit()

