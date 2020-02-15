from flask import Flask, render_template, redirect, request
import urllib.parse
from sqlalchemy import create_engine
import psycopg2
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from io import StringIO
import base64

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

app = Flask(__name__)


@app.route('/')
def index():
    query = '''SELECT * FROM census LIMIT 10;'''
    queryResult = pd.read_sql_query(query, psqlconn)
    queryResult = "To display head of the table here"
    return render_template('index.html', dbPreview=queryResult)


@app.route('/handle_submit', methods=['POST'])
def handle_submit():
    # To handle standard query
    stdQuery = request.form['stdQuery']
    stdQueryResult = pd.read_sql_query(stdQuery, psqlconn)

    # To handle adversarial query
    advQuery = request.form['advQuery']
    advQueryResult = pd.read_sql_query(advQuery, psqlconn)

    # Join the two Dataframes on `salary` and check the distributions
    jointData = pd.merge(stdQueryResult, advQueryResult, on='salary')
    jointMelt = pd.melt(jointData, id_vars="salary",
                        var_name="query", value_name="count")
    fig_std = sb.catplot(x='count', y='salary', hue='query',
                         data=jointMelt, kind='bar', height=10)

    img_std = StringIO.StringIO()
    plt.savefig(fig_std, format='png')
    plt.close()
    img_std.seek(0)
    plot_url_std = base64.b64encode(img_std.getvalue())

    # Join the two Dataframes on `salary` and check the difference
    jointData["difference"] = jointData["count_x"] - jointData["count_y"]
    fig_adv = sb.barplot(x="difference", y="salary", data=jointData)

    img_adv = StringIO.StringIO()
    plt.savefig(fig_adv, format='png')
    plt.close()
    img_adv.seek(0)
    plot_url_adv = base64.b64encode(img_adv.getvalue())

    return render_template('/plots', plot_url_std=plot_url_std, plot_url_adv=plot_url_adv)


if __name__ == "__main__":
    app.run(debug=True)
