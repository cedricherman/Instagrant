from flask import render_template
from sbir_app import app
from flask import request
from sbir_app.a_Model import ModelIt
# from sqlalchemy import create_engine
# from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

# Python code to connect to Postgres
# You may need to modify this based on your OS,
# as detailed in the postgres dev setup materials.
username = 'postgres'
password = 'viVEra23'     # change this
host     = 'localhost'
port     = '5432'            # default port that postgres listens on
db_name  = 'birth_db'
# engine = create_engine( 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, db_name) )
con = None
con = psycopg2.connect(dbname = db_name, user = username, host = host, password = password)


@app.route('/')
@app.route('/index')
def index():
   user = { 'nickname': 'Miguel' } # fake user
   return render_template("index.html", title = 'Home', user = user)
# def index():
  # return "Hello, World!"


@app.route('/db')
def birth_page():
   sql_query = """
               SELECT * FROM birth_data_table WHERE delivery_method='Cesarean';
               """
   query_results = pd.read_sql_query(sql_query,con)
   births = ""
   for i in range(0,10):
       births += query_results.iloc[i]['birth_month']
       births += "<br>"
   return births

@app.route('/db_fancy')
def cesareans_page_fancy():
   sql_query = """
              SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean';
               """
   query_results=pd.read_sql_query(sql_query,con)
   births = []
   for i in range(0,query_results.shape[0]):
       births.append(dict(index=query_results.iloc[i]['index'], attendant=query_results.iloc[i]['attendant'], birth_month=query_results.iloc[i]['birth_month']))
   return render_template('cesareans.html',births=births)


@app.route('/input')
def cesareans_input():
   return render_template("input.html")



@app.route('/output')
def cesareans_output():
 #pull 'birth_month' from input field and store it
 patient = request.args.get('birth_month')
   #just select the Cesareans  from the birth dtabase for the month that the user inputs
 query = "SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean' AND birth_month='%s'" % patient
 print(query)
 query_results=pd.read_sql_query(query,con)
 print(query_results)
 births = []
 for i in range(0,query_results.shape[0]):
     births.append(dict(index=query_results.iloc[i]['index'], attendant=query_results.iloc[i]['attendant'], birth_month=query_results.iloc[i]['birth_month']))
     the_result = ModelIt(patient,births)
 return render_template("output.html", births = births, the_result = the_result)
