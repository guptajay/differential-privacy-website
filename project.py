#!/usr/bin/python3
from flask import Flask, render_template, redirect, request
from urllib import parse
from sqlalchemy import create_engine
import psycopg2
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import io
import base64
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# Postgres Login Credentials
POSTGRES_ADDRESS = '157.230.253.111'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'postgres'
POSTGRES_PASSWORD = ''
POSTGRES_DBNAME = 'test'

# Postgres Connection String
conn_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
            .format(username=POSTGRES_USERNAME,
                    password=POSTGRES_PASSWORD,
                    ipaddress=POSTGRES_ADDRESS,
                    port=POSTGRES_PORT,
                    dbname=POSTGRES_DBNAME))

# Create the connection
psqlconn = create_engine(conn_str)

# Global Variables
stdQuery = ''
advQuery = ''

app = Flask(__name__)


@app.route('/')
def index():
    query = '''SELECT * FROM census LIMIT 10;'''
    queryResult = pd.read_sql_query(query, psqlconn)
    return render_template('index.html', dbPreview=queryResult.to_html())


@app.route('/handle_submit', methods=['POST'])
def handle_submit():
    # To handle standard query
    stdQuery = request.form['stdQuery']
    stdQueryResult = pd.read_sql_query(stdQuery, psqlconn)

    # To handle adversarial query
    advQuery = request.form['advQuery']
    advQueryResult = pd.read_sql_query(advQuery, psqlconn)

    fig, axs = plt.subplots(1,2, figsize=(12,6))

    # Join the two Dataframes on `salary` and check the distributions
    jointData = pd.merge(stdQueryResult, advQueryResult, on='salary')
    jointMelt = pd.melt(jointData, id_vars="salary",
                        var_name="query", value_name="count")
    axs[0].bar(jointMelt['salary'], jointMelt['count'])

    # Join the two Dataframes on `salary` and check the difference
    jointData["difference"] = jointData["count_x"] - jointData["count_y"]
    axs[1].bar(jointData['salary'], jointData['difference'])

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')


    return render_template('plots.html',plot_url = pngImageB64String)

if __name__ == "__main__":
    app.run(debug=True)
