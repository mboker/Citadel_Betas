from flask import Flask, render_template, url_for
from flask_restful import Resource, Api, reqparse
import sqlite3
from flask import g, request

import numpy as np
import pandas as pd
from service.company import Company

#TODO: replace this w some function to get relative path
DATABASE = '/Users/mboker/PycharmProjects/citadel_project/beta_schema.db'
alpha_vantage_key = 'LLU8D8CBCS87GWXU'

small_cap_changes, mid_cap_changes, high_cap_changes = None, None, None


def get_db(app):
    with app.app_context():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
        return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

class BetaForSymbol(Resource):
    def post(self):
        args = request.values
        symbol = args['symbol']
        market = args['market[]']

        # symbol_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
        #           '&datatype=csv&outputsize=20&symbol='+ticker_symbol+'&apikey=' + alpha_vantage_key
        # symbol_data = pd.read_csv(symbol_url,
        #                             usecols=['timestamp', 'close'])
        symbol_data = pd.read_csv(app.open_resource('data/daily_'+symbol+'.csv'),
                                    usecols=['timestamp', 'close'])

        symbol_closes = np.array(symbol_data['close'])
        symbol_diffs = -1 * np.diff(symbol_closes)
        symbol_closes = np.delete(symbol_closes, 0, 0)
        symbol_changes = np.round((symbol_diffs / symbol_closes) * 100,3)
        betas = np.linalg.lstsq(high_cap_changes[:,None], symbol_changes)[0]


        dates = list(symbol_data.timestamp)[:-1]
        return_list = [{'date': timestamp, 'value': symbol_changes[idx]} for idx, timestamp
                                    in enumerate(dates)]
        change_list = sorted(return_list, key=lambda item : item['date'])

        return {'changes':{symbol:change_list}}


class BetasForSymbols(Resource):
    def post(self):
        args = request.values
        symbols = args['symbols']
        start_date = args['start']
        end_date = args['end']

        # symbol_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
        #           '&datatype=csv&outputsize=20&symbol='+ticker_symbol+'&apikey=' + alpha_vantage_key
        # symbol_data = pd.read_csv(symbol_url,
        #                             usecols=['timestamp', 'close'])

        return_obj = {'changes':{}}
        for symbol in symbols:
            symbol_data = pd.read_csv(app.open_resource('data/daily_'+symbol+'.csv'),
                                        usecols=['timestamp', 'close'])

            symbol_closes = np.array(symbol_data['close'])
            symbol_diffs = -1 * np.diff(symbol_closes)
            symbol_closes = np.delete(symbol_closes, 0, 0)
            symbol_changes = list(np.round((symbol_diffs / symbol_closes) * 100,3))
            dates = list(symbol_data.timestamp)[:-1]
            return_list = [{'date': timestamp, 'value': symbol_changes[idx]} for idx, timestamp
                                        in enumerate(dates)]
            change_list = sorted(return_list, key=lambda item : item['date'])
            return_obj['changes'][symbol] = change_list

        return return_obj






def initialize_app():
    app = Flask(__name__)
    # high_cap_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
    #           '&datatype=csv&outputsize=20&symbol=INX&apikey=' + alpha_vantage_key
    # mid_cap_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
    #               '&datatype=csv&outputsize=full&symbol=MID&apikey=' + alpha_vantage_key
    # small_cap_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY' + \
    #                 '&datatype=csv&outputsize=full&symbol=SML&apikey=' + alpha_vantage_key
    #
    high_cap_data = pd.read_csv(app.open_resource('data/daily_INX.csv'),
                                usecols=['timestamp', 'close'])
    # mid_cap_data = pd.read_csv(mid_cap_url,
    #                             usecols=['timestamp', 'close'])
    # small_cap_data = pd.read_csv(small_cap_url,
    #                             usecols=['timestamp', 'close'])
    #
    high_cap_closes = np.array(high_cap_data['close'])
    high_cap_diffs = -1 * np.diff(high_cap_closes)
    high_cap_closes = np.delete(high_cap_closes, 0, 0)
    global high_cap_changes
    high_cap_changes = (high_cap_diffs / high_cap_closes) * 100
    #
    # mid_cap_closes = np.array(mid_cap_data['close'])
    # mid_cap_diffs = -1 * np.diff(mid_cap_closes)
    # mid_cap_closes = np.delete(mid_cap_closes, 0, 0)
    # mid_cap_changes = (mid_cap_diffs / mid_cap_closes) * 100
    #
    # small_cap_closes = np.array(small_cap_data['close'])
    # small_cap_diffs = -1 * np.diff(small_cap_closes)
    # small_cap_closes = np.delete(small_cap_closes, 0, 0)
    # small_cap_changes = (small_cap_diffs / small_cap_closes) * 100
    get_db(app)
    return app
app = initialize_app()
api = Api(app)

api.add_resource(BetaForSymbol, '/beta')
api.add_resource(BetasForSymbols, '/betas')
api.add_resource(Company, '/companies')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html',
                           header_one='The first header')#TODO Replace or remove this param - only meant as example


if __name__ == '__main__':
    app.run()
