import pandas as pd
import numpy as np

from flask import request, render_template, url_for
from pymongo import MongoClient
from sbir_app import app, agency_name, agency_logo, gs_reg


# Create a client connection to the MongoDb instance running on the local machine
client = MongoClient('localhost:27017')
# connect to database of interest
db = client.awards_tmp


@app.route('/')
@app.route('/home')
def home_select_agency():
     return render_template("home.html")


@app.route('/input')
def text_input():
     # retrieve agency identifier
     agency_id = request.args.get('type')

     return render_template("input.html",
                        agency = agency_name[agency_id],
                        agency_logo = agency_logo[agency_id],
                        agency_id = agency_id)



@app.route('/output')
def cesareans_output():
     #pull 'birth_month' from input field and store it
     text = request.args.get('abstract')
     # print(text)

     # model id is the federal agency abbreviation
     model_id = request.args.get('model_id')
     # print(model_id)

     # make prediction
     dollars = gs_reg.predict([text])[0]
     # dollars = federal_m[model_id].predict([text])[0]


     # percentile = model_id
     # cursor_tmp is a generator
     cursor_tmp = db.awards_tmp.find({'Agency' : agency_name[model_id],
                         'Phase' : 'Phase I'},
                             {'amount_corrected' : 1,
                             'company name' : 1,
                             '_id': False} )

     # need a new cursor (generator) after you used it
     df = pd.DataFrame(list(cursor_tmp))

     # calculate percentile (ecdf)
     pl_x = df.amount_corrected.sort_values().values
     pl_y = np.arange(1, len(pl_x)+1) / len(pl_x)
     # get corresponding quantile to dollar amount
     percentile = pl_y[pl_x <= dollars].max()

     return render_template("output.html",
                            the_result = '$ {:,.0f}'.format(dollars),
                            percentile = '{:.0f}th percentile'.format(percentile*100) )
