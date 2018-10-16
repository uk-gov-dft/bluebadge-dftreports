#!/usr/bin/python
import psycopg2
import os
import urlparse
import json
import time
from datetime import date
from datetime import timedelta

from flask import Flask, render_template, request

from config import config

class LA_Count(object):

    def __init__(self, la, count):
        self.la = la
        self.count = count

class ViewModel(object):

    def __init__(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.rows = ()
        self.summary = self.__generate_summary__()

    def add(self, la_count):
        self.rows = self.rows + (la_count,)
        self.summary = self.__generate_summary__()

    def __generate_summary__(self):
        return "Between {} and {} : {} Local Authorities".format(self.from_date, self.to_date, len(self.rows))

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
    db = "dbname=%s user=%s  ***REMOVED*** host=%s " % (url.path[1:], url.username, url.password, url.hostname)
    conn = psycopg2.connect(db)
    cur = conn.cursor()

    # a simple page that says hello
    @app.route('/applications')
    def application_count():
        default_from = date.today()
        default_to = default_from + timedelta(days=1)
        
        from_date = request.args.get('from') or default_from.isoformat()
        to_date = request.args.get('to') or default_to.isoformat()

        statement = """select local_authority_code, count(local_authority_code) from applicationmanagement.application
                where submission_datetime 
                between %s and %s
                group by local_authority_code;"""
 
        # display the PostgreSQL database server version
        cur.execute(statement, (from_date, to_date))
        data = cur.fetchall()
        view_model = ViewModel(from_date, to_date)
        for item in data:
            view_model.add(LA_Count(item[0], item[1]))

        return render_template('template.html',  view_model=view_model)
    return app
 
 
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
