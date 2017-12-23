from flask import Flask, render_template
from flask_restful import Resource, Api
from flask import g, request, make_response
import pandas as pd
from service import calculator
import sqlite3

alpha_vantage_key = 'LLU8D8CBCS87GWXU'
quandl_key = '5MzkPyT6BEVVv3u9-kkH'
DATABASE = 'beta_schema.db'

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


class Company(Resource):
    def get(self):
        args = request.args
        # companies = company.get_companies(query_string)
        query_string = args['q']
        companies = get_companies(query_string)
        return {'companies' : companies}


def get_companies(query_string):
    cur = get_company_db().cursor()
    cur.execute("select SYMBOL AS id, NAME, SYMBOL || ' - ' || NAME AS DISPLAY " +
                "from COMPANY where NAME like '%"+query_string + "%' or " +
                "symbol like '%"+query_string+"%'")
    rows = cur.fetchall()
    return rows


def initialize_app():
    app = Flask(__name__)
    global market
    market = pd.read_csv(app.open_resource('data/dailies/market.csv'),
                                usecols=['timestamp', 'close'], parse_dates=['timestamp'], index_col='timestamp')
    market.columns = ['MKT']
    return app


def get_company_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.root_path+'/'+DATABASE)
    db.row_factory = make_dicts
    return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


app = initialize_app()
with app.app_context():
    get_company_db()
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
