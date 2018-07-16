from pymongo import MongoClient
import os
import glob
import json
import re


# Create a client connection to the MongoDb instance running on the local machine
client = MongoClient('localhost:27017')

# define a database object to insert data into the MongoDb database
db = client.awards_tmp

json_award_year = glob.glob(os.path.join(os.pardir, 'data', 'interim', '*.json'))

for jfile in json_award_year:

    # load list of dictionaries
    with open(jfile) as f:
        year = json.load(f)

    # convert amount to integer
    for y in year:

        # retrieve dollar amount from dictionary y
        amount_str = y.get('Amount', 'N/A')

        # remove characters expect digits and period
        amount_digit = re.sub('[^\d.]', '', amount_str)

        # check if there are any numbers in amount_digit
        if not not amount_digit:
            y['Amount'] = float(amount_digit)

    # insert all records
    db.awards_tmp.insert_many(year)

# take current count
db.awards_tmp.count()

db.collection_names()

### Remove Branch and Agency field when it is missing (N/A)
# remove N/A Branch field
db.awards_tmp.update_many({ 'Branch': 'N/A' }, {'$unset': {'Branch':1}})

# remove N/A agency field
db.awards_tmp.update_many({ 'Agency': 'N/A' }, {'$unset': {'Agency':1}})




## Compute amount corrected for inflation

# cursor_tmp is a generator
cursor_tmp = db.awards_tmp.find({}, {'Amount' : 1,
                                     'Awards Year' : 1,
                                     '_id': True} )
# need a new cursor (generator) after you used it
df = pd.DataFrame(list(cursor_tmp))

# convert Awards year to datetime object
df['Awards Year'] = pd.to_datetime(df['Awards Year'])

# consumer price index
infl_dir = os.path.join(os.pardir, 'data', 'external', 'SeriesReport-20180624222036_5126de.xlsx')
# first 23 rows are skipped, first column are dates which I used as index
df_infl = pd.read_excel(infl_dir, header=0, skiprows=range(1, 12), parse_dates=True, index_col=0)

# average CPI for each year is in 3rd to last column
# average CPI for 2018 (last row) has not been calculated (not all months are there yet!)
# so I calculated it myself
df_infl.iloc[-1,-3] = df_infl.iloc[-1, :-3].mean()

# only keep annual average CPI
s_infl = df_infl.iloc[:,-3]

# normalized CPI by last available year (2018)
s_infl = s_infl/s_infl[-1]

# add CPI correction factor to my dataframe
df['inflation_factor'] = df['Awards Year'].map(s_infl)

# add corrected dollar amount column
df['amount_corrected'] = df.Amount.divide(df.inflation_factor)

### Add inflation corrected amount to DB

for index, row in df.loc[:, ['_id', 'amount_corrected']].iterrows():
    db.awards_tmp.update_one({"_id" : row['_id'] },
                         {"$set" : {"amount_corrected": row['amount_corrected'] }})
