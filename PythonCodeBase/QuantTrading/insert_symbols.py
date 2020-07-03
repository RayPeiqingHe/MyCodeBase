#!/usr/bin/python
# -*- coding: utf-8 -*-

# insert_symbols.py

import datetime

import bs4
import MySQLdb as mdb
import requests
from configparser import ConfigParser
import pandas as pd
import numpy as np


# Connect to the MySQL instance

parser = ConfigParser()
parser.read('db.ini')

# Connect to the MySQL instance
db_host = parser.get('mysql', 'host')
db_name = parser.get('mysql', 'db')
db_user = parser.get('mysql', 'username')
db_pass = parser.get('mysql', 'password')


def obtain_parse_wiki_snp500(existing_tickers):
    """
    Download and parse the Wikipedia list of S&P500
    constituents using requests and BeautifulSoup.

    Returns a list of tuples for to add to MySQL.
    """
    # Stores the current time, for the created_at record
    now = datetime.datetime.utcnow()

    # Use requests and BeautifulSoup to download the
    # list of S&P500 companies and obtain the symbol table
    response = requests.get(
        "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )
    soup = bs4.BeautifulSoup(response.text, "lxml")

    # This selects the first table, using CSS Selector syntax
    # and then ignores the header row ([1:])
    symbolslist = soup.select('table')[0].select('tr')[1:]

    # Obtain the symbol information for each
    # row in the S&P500 constituent table
    symbols = []
    for i, symbol in enumerate(symbolslist):
        tds = symbol.select('td')

        ticker = tds[0].select('a')[0].text

        if ticker in existing_tickers:
            continue

        symbols.append(
            (
                '1',
                tds[0].select('a')[0].text,  # Ticker
                'stock',
                tds[1].select('a')[0].text,  # Name
                tds[3].text,  # Sector
                'USD', now, now
            )
        )
    return symbols


def obtain_parse_nasdaq100(existing_tickers):
    from pytickersymbols import PyTickerSymbols

    stock_data = PyTickerSymbols()

    nasdaq100_stocks = stock_data.get_stocks_by_index('NASDAQ 100')

    nasdaq_symbols = []
    for symbol in nasdaq100_stocks:
        ticker = symbol['symbol']

        if ticker not in existing_tickers:
            nasdaq_symbols.append(
                (
                    '2',
                    ticker,  # Ticker
                    'stock',
                    symbol['name'],  # Name
                    symbol['industries'][0],  # Sector
                    'USD',
                    datetime.datetime.utcnow(),
                    datetime.datetime.utcnow()
                )
            )

    return nasdaq_symbols


def get_existing_symbols_from_db():
    """
    Pull the existing symbols from SQL db

    :return:
    """
    con = mdb.connect(
        host=db_host, user=db_user, password=db_pass, db=db_name
    )

    sql_query = "select ticker from symbol"

    with con:
        with con.cursor() as cur:
            cur.execute(sql_query)
            data = cur.fetchall()

    return set([d[0] for d in data])


def insert_snp500_symbols(symbols):
    """
    Insert the S&P500 symbols into the MySQL database.
    """

    con = mdb.connect(
        host=db_host, user=db_user, password=db_pass, db=db_name
    )

    # Create the insert strings
    column_str = """exchange_id, ticker, instrument, name, sector,
                 currency, created_date, last_updated_date
                 """
    insert_str = ("%s, " * 8)[:-2]
    final_str = "INSERT INTO symbol (%s) VALUES (%s)" % \
        (column_str, insert_str)

    # Using the MySQL connection, carry out
    # an INSERT INTO for every symbol
    with con:
        cur = con.cursor()
        cur.executemany(final_str, symbols)


def getNasdaqTickersFromCsv(existing_nasdaq_tickers, csv_file='companylist.csv'):
    df_tickers = pd.read_csv(csv_file)

    df_tickers.replace(np.nan, '', inplace=True, regex=True)

    nasdaq_symbols = []
    for index, symbol in df_tickers.iterrows():
        ticker = symbol['Symbol']

        if ticker not in existing_nasdaq_tickers:
            nasdaq_symbols.append(
                (
                    '3',
                    ticker,  # Ticker
                    'stock',
                    symbol['Name'],  # Name
                    symbol['industry'],  # Sector
                    'USD',
                    datetime.datetime.utcnow(),
                    datetime.datetime.utcnow()
                )
            )

    return nasdaq_symbols


if __name__ == "__main__":

    existing_tickers = get_existing_symbols_from_db()

    symbols = obtain_parse_wiki_snp500(existing_tickers)

    if len(symbols) > 0:
        insert_snp500_symbols(symbols)

        print('The following new symbols are inserted')
        print('\n'.join([s[1] for s in symbols]))

    existing_tickers = existing_tickers | set(symbols)

    symbols = obtain_parse_nasdaq100(existing_tickers)

    existing_tickers = existing_tickers | set(symbols)

    symbols = getNasdaqTickersFromCsv(existing_tickers)

    if len(symbols) > 0:
        insert_snp500_symbols(symbols)

        print('The following new symbols are inserted')
        print('\n'.join([s[1] for s in symbols]))

    print("%s symbols were successfully added." % len(symbols))
