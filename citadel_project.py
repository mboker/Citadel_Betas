from flask import Flask, render_template
from flask_restful import Resource, Api
from flask import g, request, make_response
import pandas as pd
from service.company import Company
from service import calculator

alpha_vantage_key = 'LLU8D8CBCS87GWXU'

market = None


class BetasForSymbols(Resource):
    def post(self):
        form = request.form
        start_date = form['start']
        end_date = form['end']
        symbols = form.getlist('symbols[]')

        collection = market.copy()
        for symbol in symbols:
            stock = pd.read_csv(app.open_resource('data/dailies/daily_'+symbol+'.csv'),
                                 usecols=['timestamp', 'close'], parse_dates=['timestamp'],index_col='timestamp')
            stock.columns = [symbol]
            collection = collection.join(stock)

        collection = collection[end_date:start_date]
        columns = list(collection)
        columns.remove('MKT')
        collection['Portfolio'] = collection[columns].sum(axis=1)
        betas = calculator.calculate(collection,30)
        return make_response(betas.to_json(orient='columns', date_format='iso'))


def initialize_app():
    app = Flask(__name__)
    global market
    market = pd.read_csv(app.open_resource('data/dailies/daily_INX.csv'),
                                usecols=['timestamp', 'close'], index_col='timestamp')
    market.columns = ['MKT']
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
    return render_template('index.html',
                           header_one='The first header')#TODO Replace or remove this param - only meant as example


if __name__ == '__main__':
    app.run()
