import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
import sys

alpha_vantage_key = 'LLU8D8CBCS87GWXU'

def get_data(symbol):
    try_again = True
    while try_again:
        try:
            try_again = False
            symbol = symbol.strip()
            symbol_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
                       '&datatype=csv&outputsize=full&symbol='+symbol+'&apikey=' + alpha_vantage_key
            symbol_data = pd.read_csv(symbol_url, usecols=['timestamp', 'close'])
            symbol_data.to_csv('data/dailies/daily_'+symbol+'.csv')
            return True
        except UnicodeEncodeError as e:
            print(symbol)
            print(e)
            return False
        except ValueError as ve:
            #alphavantage app failed to serve, so try again
            try_again = True
        except Exception as e:
            print(symbol)
            print(e)
            return False
    return False

pool = ThreadPool(400)
symbols = list(pd.read_csv('data/market_symbols.csv',header=None)[0])

results = pool.map(get_data, symbols)

pool.close()
pool.join()

sys.exit()