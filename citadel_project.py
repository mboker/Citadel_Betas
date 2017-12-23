from flask import Flask, render_template
from flask_restful import Resource, Api
from flask import g, request, make_response
import pandas as pd
from service.company import Company
from service import calculator
import sqlite3

alpha_vantage_key = 'LLU8D8CBCS87GWXU'
quandl_key = '5MzkPyT6BEVVv3u9-kkH'

market = None


#https://www.quandl.com/api/v3/datatables/WIKI/PRICES.csv?symbol=AAPL&api_key=5MzkPyT6BEVVv3u9-kkH


class BetasForSymbols(Resource):
    def post(self):
        form = request.form
        start_date = form['start']
        end_date = form['end']
        symbols = form.getlist('symbols[]')
        window = int(form['window'])

        collection = market.copy()
        for symbol in symbols:
            stock = pd.read_csv(app.open_resource('data/dailies/daily_'+symbol+'.csv'),
                        usecols=['timestamp', 'close'], parse_dates=['timestamp'],index_col='timestamp').sort_index()
            stock.columns = [symbol]
            collection = collection.join(stock, how='inner')

        collection = collection[start_date:end_date]
        betas = calculator.calculate(collection, window)
        return make_response(betas.to_json(orient='columns', date_format='iso'))


def get_db(app):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app)
    db.row_factory = make_dicts
    return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def initialize_app():
    app = Flask(__name__)
    global market
    market = pd.read_csv(app.open_resource('data/dailies/market.csv'),
                                usecols=['timestamp', 'close'], parse_dates=['timestamp'], index_col='timestamp')
    market.columns = ['MKT']
    get_db(app)
    return app


app = initialize_app()
api = Api(app)
api.add_resource(BetasForSymbols, '/betas')
api.add_resource(Company, '/companies')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
