#!/usr/bin/python
# -*- coding: utf-8 -*-

# price_retrieval.py

from __future__ import print_function

import datetime
import warnings

import MySQLdb as mdb
import requests
from ConfigParser import SafeConfigParser
from decimal import Decimal
from sqlalchemy import create_engine
import pandas as pd
from pandas_datareader._utils import RemoteDataError


# Obtain a database connection to the MySQL instance
# Connect to the MySQL instance
parser = SafeConfigParser()
parser.read('config.ini')

# Connect to the MySQL instance
db_host = parser.get('log_in', 'host')
db_name = parser.get('log_in', 'db')
db_user = parser.get('log_in', 'username')
db_pass = parser.get('log_in', 'password')


def obtain_list_of_db_tickers(sql_query):
    """
    Obtains a list of the ticker symbols in the database.
    """
    con = mdb.connect(
        host=db_host, user=db_user, password=db_pass, db=db_name
    )

    with con:
        with con.cursor() as cur:
            cur.execute(sql_query)
            data = cur.fetchall()

    return [(d[0], d[1], d[2]) for d in data]


def get_daily_historic_data_pandas(
        ticker, start_date=(2000, 1, 1),
        end_date=datetime.date.today(),
        source='yahoo'):
    import pandas_datareader.data as web

    res = web.DataReader(ticker, source, start_date, end_date)

    res.reset_index(inplace=True)

    column_map = {
        'Date': 'price_date',
        'Open': 'open_price',
        'High': 'high_price',
        'Low': 'low_price',
        'Close': 'close_price',
        'Adj Close': 'adj_close_price',
        'Volume': 'volume'
        }

    res.rename(index=str, columns=column_map, inplace=True)

    return res


def get_daily_historic_data_yahoo(
        ticker, start_date=(2000, 1, 1),
        end_date=datetime.date.today().timetuple()[0:3]
        ):
    """
    Obtains data from Yahoo Finance returns and a list of tuples.

    ticker: Yahoo Finance ticker symbol, e.g. "GOOG" for Google, Inc.
    start_date: Start date in (YYYY, M, D) format
    end_date: End date in (YYYY, M, D) format
    """
    # Construct the Yahoo URL with the correct integer query parameters
    # for start and end dates. Note that some parameters are zero-based!
    ticker_tup = (
        ticker, start_date[1]-1, start_date[2],
        start_date[0], end_date[1]-1, end_date[2],
        end_date[0]
    )
    yahoo_url = "http://ichart.finance.yahoo.com/table.csv"
    yahoo_url += "?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s"
    yahoo_url = yahoo_url % ticker_tup

    # Try connecting to Yahoo Finance and obtaining the data
    # On failure, print an error message.

    prices = []

    try:
        yf_data = requests.get(yahoo_url).text.split("\n")[1:-1]

        for y in yf_data:
            p = y.strip().split(',')
            prices.append(
                (
                    datetime.datetime.strptime(p[0], '%Y-%m-%d'),
                    p[1], p[2], p[3], p[4], p[5], p[6])
                )
    except Exception as ex:
        print("Could not download Yahoo data: %s" % ex)
    return prices


def get_corporate_action_from_yahoo(
        ticker, start_date=(2000, 1, 1),
        end_date=datetime.date.today().timetuple()[0:3]
        ):
    ticker_tup = (
        ticker, start_date[1]-1, start_date[2],
        start_date[0], end_date[1]-1, end_date[2],
        end_date[0]
    )

    yahoo_url = "http://ichart.finance.yahoo.com/x"
    yahoo_url += "?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&g=v&y=0&z=30000"
    yahoo_url = yahoo_url % ticker_tup

    corporate_actions = []
    try:
        yf_data = requests.get(yahoo_url).text.split("\n")[1:-5]

        for y in yf_data:
            p = y.strip().split(',')

            corporate_actions.append(
               (p[0], datetime.datetime.strptime(p[1].strip(), '%Y%m%d'), Decimal(p[2].split(':')[0])
                   if p[0] == 'SPLIT' else Decimal(p[2]), Decimal(p[2].split(':')[1])
                   if p[0] == 'SPLIT' else 0))
    except Exception as ex:
        print("Could not download Yahoo data: %s" % ex)
    return corporate_actions


def insert_daily_data_into_db_from_df(
        df_prices,
        ticker,
        table_name='daily_price',
        data_vendor_id=1,
        symbol_id=None):
    conn_str = 'mysql://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_name)

    engine = create_engine(conn_str)

    query = "SELECT id FROM symbol WHERE ticker = '{0}'".format(ticker)

    with engine.connect() as conn, conn.begin():
        if symbol_id is None:
            symbol_id = pd.read_sql_query(query, engine).iloc[0]['id']

        df_prices['symbol_id'] = symbol_id
        df_prices['data_vendor_id'] = data_vendor_id

        df_prices.to_sql(table_name, conn, if_exists='append', index=False)

        df_prices.drop(['symbol_id'], axis=1)


def insert_daily_data_into_db(
        data_vendor_id, symbol_id, daily_data
        ):
    """
    Takes a list of tuples of daily data and adds it to the
    MySQL database. Appends the vendor ID and symbol ID to the data.

    daily_data: List of tuples of the OHLC data (with
    adj_close and volume)
    """
    # Create the time now
    now = datetime.datetime.utcnow()

    # Amend the data to include the vendor ID and symbol ID
    daily_data = [
        (data_vendor_id, symbol_id, d[0], now, now,
            d[1], d[2], d[3], d[4], d[5], d[6])
        for d in daily_data
    ]

    # Create the insert strings
    insert_str = ("%s, " * 11)[:-2]

    final_str = "EXEC dbo.sp_insert_daily_price %s" % insert_str

    con = mdb.connect(
        host=db_host, user=db_user, password=db_pass, db=db_name
    )

    # Using the MySQL connection, carry out an INSERT INTO for every symbol
    with con:
        with con.cursor() as cur:
            cur.executemany(final_str, daily_data)


def insert_corporate_action_data_into_db(
        data_vendor_id, symbol_id, corporate_action_data, last_data_date
        ):
    """
    Takes a list of tuples of daily data and adds it to the
    MySQL database. Appends the vendor ID and symbol ID to the data.

    daily_data: List of tuples of the OHLC data (with
    adj_close and volume)
    """
    # Create the time now
    now = datetime.datetime.utcnow()

    # Amend the data to include the vendor ID and symbol ID
    corporate_action_data = [
        (data_vendor_id, symbol_id, d[1], now, now,
            d[0], d[2], d[3])
        for d in corporate_action_data if d[1] > last_data_date
    ]

    if len(corporate_action_data) == 0:
        return

    # Create the insert strings
    column_str = """data_vendor_id, symbol_id, corporate_action_date, created_date,
                 last_updated_date, corporate_action_type,
                 prior_amount, ex_amount"""
    insert_str = ("%s, " * 8)[:-2]
    final_str = "INSERT INTO corporate_action (%s) VALUES (%s)" % \
        (column_str, insert_str)

    con = mdb.connect(
        host=db_host, user=db_user, password=db_pass, db=db_name
    )

    # Using the MySQL connection, carry out an INSERT INTO for every symbol
    with con:
        with con.cursor() as cur:
            cur.executemany(final_str, corporate_action_data)


def get_command_line_args():
    """Read the all required inputs from the command line argument"""

    import argparse

    # Parse the command line argument
    parser = argparse.ArgumentParser(description='Yahoo Data downloader')

    # Add argument for the input amount
    # The command line argument for API key
    parser.add_argument('-t', action="store", dest="t", type=str, const=None, default='p',
                        help="Data Type to download: p for daily prices and d for corporate actions")

    cmd_args = parser.parse_args()

    # Return all command line arguments
    return cmd_args


if __name__ == "__main__":
    # This ignores the warnings regarding Data Truncation
    # from the Yahoo precision to Decimal(19,4) datatypes
    warnings.filterwarnings('ignore')

    args = get_command_line_args()

    # Loop over the tickers and insert the daily historical
    # data into the database

    if args.t == 'p':
        security_query = "SELECT * FROM vw_last_missing_price_date WHERE last_price_date = '2000-01-01' ORDER BY ticker"
    else:
        security_query = "SELECT * FROM vw_last_missing_corporate_action_date ORDER BY ticker"

    tickers = obtain_list_of_db_tickers(security_query)

    lentickers = len(tickers)
    for i, t in enumerate(tickers):
        print(
            "Adding data for %s: %s out of %s %s" %
            (t[1], i+1, lentickers, t[2][:10])
        )

        try:
            if args.t == 'p':

                s_date = datetime.datetime.strptime(t[2][:10], '%Y-%m-%d')

                e_date = datetime.date.today()

                df_res = get_daily_historic_data_pandas(t[1],
                                                            s_date, e_date, 'yahoo')

                if len(df_res.index) > 0 and df_res.iloc[-1]['price_date'] > s_date:
                        insert_daily_data_into_db_from_df(df_res, t[1], symbol_id=t[0])
            else:
                yahoo_data = get_corporate_action_from_yahoo(
                    t[1],
                    start_date=datetime.datetime.strptime(t[2], '%Y-%m-%d').timetuple()[0:3])

                insert_corporate_action_data_into_db('1', t[0], yahoo_data,
                                                        datetime.datetime.strptime(t[2], '%Y-%m-%d'))

        except RemoteDataError as e:
            print(e)

    print("Successfully added Yahoo Finance pricing data to DB.")
