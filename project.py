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
    columns = list(queryResult)
    return render_template('index.html', dbPreview=queryResult.to_html(), dataset_name="census", flag=0, columns=columns)


@app.route('/change_dataset', methods=['POST'])
def change_dataset():
    dataset_name = request.form['dataset']
    query = '''SELECT * FROM ''' + dataset_name + ''' LIMIT 10;'''
    queryResult = pd.read_sql_query(query, psqlconn)
    columns = list(queryResult)
    return render_template('index.html', dbPreview=queryResult.to_html(), dataset_name=dataset_name, flag=1, columns=list(queryResult))


@app.route('/generate_graphs', methods=['POST'])
def generate_graphs():
    # To handle
    hiRitik = 'complete the code from here'


@app.route('/handle_submit', methods=['POST'])
def handle_submit():
    # To handle standard query
    stdQuery = request.form['stdQuery']

    # To handle adversarial query
    advQuery = request.form['advQuery']

    # If only advQuery
    if(len(stdQuery) <= 1 and len(advQuery) > 1):
        advQueryResult = pd.read_sql_query(advQuery, psqlconn)
        fig, axs = plt.subplots(1, 1, figsize=(15, 5))
        axs.bar(advQueryResult['salary'], advQueryResult['count'])
        axs.set_title('Adversarial Query')

    # If both are present
    elif(len(stdQuery) > 1 and len(advQuery) > 1):
        stdQueryResult = pd.read_sql_query(stdQuery, psqlconn)
        advQueryResult = pd.read_sql_query(advQuery, psqlconn)

        fig, axs = plt.subplots(3, 1, figsize=(15, 15))
        axs[0].bar(stdQueryResult['salary'], stdQueryResult['count'])
        axs[0].set_title('Standard Query')
        axs[1].bar(advQueryResult['salary'], advQueryResult['count'])
        axs[1].set_title('Adversarial Query')

        # Join the two Dataframes on `salary` and check the distributions
        jointData = pd.merge(stdQueryResult, advQueryResult, on='salary')

        # Join the two Dataframes on `salary` and check the difference
        jointData["difference"] = jointData["count_x"] - jointData["count_y"]
        axs[2].bar(jointData['salary'], jointData['difference'])
        axs[2].set_title('Difference')

    # If only standard query
    else:
        stdQueryResult = pd.read_sql_query(stdQuery, psqlconn)
        fig, axs = plt.subplots(1, 1, figsize=(15, 5))
        axs.bar(stdQueryResult['salary'], stdQueryResult['count'])
        axs.set_title('Standard Query')

    fig.tight_layout()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')

    return render_template('plots.html', plot_url=pngImageB64String, stdQuery=stdQuery, advQuery=advQuery)


if __name__ == "__main__":
    app.run(debug=True)
