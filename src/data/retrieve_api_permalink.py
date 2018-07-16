import os
import requests
import warnings


def collect_api_award_data(year_range):
    """
        Collect award data through sbir api
        Save one json file per year
    """

    # url for SBIR api, outputs json data
    url = 'https://www.sbir.gov/api/awards.json'

    # collect all award year by year
    for y in year_range:

        # year is a keyword parameter for the api
        params = {'year': y}

        # request content
        r = requests.get(url, params = params)

        # check response status, 200 is good
        if r.status_code == 200:
            # construct complete file path
            json_file = '{}.json'.format(y)
            output_dir = os.path.join(os.pardir, os.pardir,'data', 'raw', json_file)

            # save json data directly to binary file
            # (e.g. no need to deserialize and serialize again)
            with open(output_dir, "wb") as f:
                f.write(r.content)

        else:
            # give warning feedback
            warnings.warn('API request failed at year {} with status code {}'.format(y, r.status_code), UserWarning)
            # write failed year to file
            with open('api_request_failure.txt', "a") as fpr:
                failed_year = '{},{}\n'.format( y, r.status_code )
                fpr.write( failed_year )



if __name__ == "__main__":

    # contruct year range
    start_year = 1983
    stop_year = 2018
    years = range(start_year,stop_year+1)

    collect_api_award_data(years)
