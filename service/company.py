from flask_restful import Resource
from flask import g, request
import sqlite3

#TODO: replace this w some function to get relative path
DATABASE = 'beta_schema.db'


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


def get_company_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))