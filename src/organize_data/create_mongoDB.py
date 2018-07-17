import glob
import json
import os
import pandas as pd
import re

from pymongo import MongoClient



def get_inflation_correction(cpi_file):
    """
        Read Consumer Price Index (CPI) from external data (downloaded from the US Bureau of Statistics)
        Normalize correction factor by last available year.
        Note that we have monthly CPI, here we take the average CPI for each year.
    """
    # consumer price index
    infl_dir = os.path.join(os.pardir, 'data', 'external', cpi_file)
    # first 23 rows are skipped, first column are dates which I used as index
    df_infl = pd.read_excel(infl_dir, header=0, skiprows=range(1, 12), parse_dates=True, index_col=0)

    # average CPI for each year is in 3rd to last column
    # average CPI for 2018 (last row) has not been calculated (not all months are there yet!)
    # so I calculated it myself below
    df_infl.iloc[-1,-3] = df_infl.iloc[-1, :-3].mean()

    # only keep annual average CPI
    s_infl = df_infl.iloc[:,-3]

    # normalized CPI by last available year (2018)
    s_infl = s_infl/s_infl[-1]

    # return year-to-correction factor mapping
    return s_infl




def add_inflated_dollar_amount(db):
    """
        Calculate dollar amount corrected for inflation using Consumer Price Index (CPI)
        from the US Bureau of Statistics.
        Add inflation corrected USD to database.
    """
    # cursor_tmp is a generator
    cursor_tmp = db.awards.find({}, {'Amount' : 1,
                                     'Awards Year' : 1,
                                     '_id': True} )
    # need a new cursor (generator) after you used it
    df = pd.DataFrame(list(cursor_tmp))

    # convert Awards year to datetime object
    df['Awards Year'] = pd.to_datetime(df['Awards Year'])

    # recover inflation correction factor
    s_infl = get_inflation_correction('SeriesReport-20180624222036_5126de.xlsx')

    # add CPI correction factor to my dataframe
    df['inflation_factor'] = df['Awards Year'].map(s_infl)

    # add corrected dollar amount column
    df['amount_corrected'] = df.Amount.divide(df.inflation_factor)

    # Add inflation corrected amount to DB
    for index, row in df.loc[:, ['_id', 'amount_corrected']].iterrows():
        db.awards.update_one({"_id" : row['_id'] },
                             {"$set" : {"amount_corrected": row['amount_corrected'] }})


def populate_db(db, json_files):
    """
        Insert content of each json file into database db
        Dollar amount if any is converted to a floating point
    """
    for jfile in json_files:

        # load list of dictionaries from this file
        with open(jfile) as f:
            year = json.load(f)

        # convert amount to integer
        for y in year:

            # retrieve dollar amount from dictionary y
            amount_str = y.get('Amount', 'N/A')

            # remove characters (like $ and comma) expect digits and period
            amount_digit = re.sub('[^\d.]', '', amount_str)

            # check if amount_digit is NOT empty before you replace it value
            if not not amount_digit:
                y['Amount'] = float(amount_digit)

        # insert all records for that file
        db.awards.insert_many(year)



if __name__ == "__main__":

    # Create a client connection to the MongoDb instance running on the local machine
    client = MongoClient('localhost:27017')

    # define a database object to insert data into
    db = client.awards_obj

    # collect all json files from web scraper
    json_award_year = glob.glob(os.path.join(os.pardir, os.pardir, 'data', 'interim', '*.json'))
    # add data from json files collected via web scraper
    populate_db(db, json_award_year)

    # Remove fields with missing values such as 'N/A'. Agency and Branch have those fields.
    db.awards.update_many({ 'Branch': 'N/A' }, {'$unset': {'Branch':1}})
    db.awards.update_many({ 'Agency': 'N/A' }, {'$unset': {'Agency':1}})

    # Compute amount corrected for inflation
    add_inflated_dollar_amount(db)
