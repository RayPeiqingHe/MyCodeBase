__author__ = 'Ray'

from FutureCaseStudy import *

import QuandlUtils as q

from datetime import datetime


def parser_datetime(input):
    """Function to parse the string into date"""

    if input is None:
        return None

    return datetime.strptime(input , '%Y-%m-%d')

def get_api_key():
    """Read the API key from the command line argument"""

    import argparse

    # Parse the command line argument
    parser = argparse.ArgumentParser(description='Quandl Utils tester')

    # Add argument for the input amount
    # The command line argument for API key
    parser.add_argument('-k', action="store", dest="k", type=str, const=None, help="Quandl API key")

    # The command line argument for start date
    parser.add_argument('-s', action="store", dest="s", type=parser_datetime, const=None, help="Start date of the query")

    # The command line argument for end date
    parser.add_argument('-d', action="store", dest="d", type=parser_datetime, const=None, help="End Date of the query")

    args = parser.parse_args()

    print args.s

    # Read the API key from the command line argument
    return args.k

def setup_quandl_query():
    """This function sets up the Quandl codes to be used in pull data"""

    # The column position of last price in the future price table
    LAST_POS = 4

    # The column position of the Total Reportable Longs column in the CTR table
    TOT_LONG = 13

    # The column position of the Total Reportable Shorts column in the CTR table
    TOT_SHORT = 14

    # Soybean future contract Quandl code: CHRIS/CME_S1
    soy_price = 'CHRIS/CME_S1'

    # Soybean Oil Futures Quandl code: CHRIS/CME_BO1
    soy_oil_price = 'CHRIS/CME_BO1'

    # Soybeans CTR Quandl code: CFTC/S_F_ALL
    soy_CTR = 'CFTC/S_F_ALL'

    # Soybeans oil CTR Quandl code: CFTC/BO_F_ALL
    soy_oil_CTR = 'CFTC/BO_F_ALL'

    # initialize the query object for future prices
    future_price_query = q.QuandlCodeHelper([soy_price, soy_oil_price], [LAST_POS])

    # initialize the query object for CTR data
    CTR_query = q.QuandlCodeHelper([soy_CTR, soy_oil_CTR], [TOT_LONG, TOT_SHORT])

    return (future_price_query, CTR_query)

def main():
    """
    A simple driver method to test the function of FutureCaseStudy
    """

    # Read the API key from the command line argument
    key = get_api_key()

    query = setup_quandl_query()

    # initialize the query object for future prices
    future_price_query = query[0]

    # initialize the query object for CTR data
    CTR_query = query[1]

    start_dt = datetime.strptime('2015-01-01' , '%Y-%m-%d')

    end_dt = datetime.strptime('2015-11-10' , '%Y-%m-%d')

    cols = ['Soybean', 'Soybean_oil']

    # Initialize the case study object
    study = FutureCaseStudy(api_key=key)

    df_prices = study.get_future_price(future_price_query.get_query_cols(), cols, start_dt=start_dt, end_dt= end_dt)

    df_soybean_ctr = study.get_ctr(CTR_query.get_query_cols(), cols, start_dt=start_dt, end_dt= end_dt)



    # 3. Visualize the raw data in python, we would like to see two charts for each commodity
    study.visualize_data(df_prices, df_soybean_ctr, cols)



    # 4. Calculate correlation for daily returns between soybean and soybean oil
    corr = study.compute_corr(df_prices, [cols[0] + '_daily_ret', cols[1] + '_daily_ret'])

    print corr

if __name__ == '__main__':
    main()
