from flask_restful import Resource
from flask import g, request
import sqlite3


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
    return db
