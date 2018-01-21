#!/usr/bin/python
# -*- coding: utf-8 -*-

# retrieving_data.py

from __future__ import print_function

import pandas as pd
# import pymssql as mdb
import MySQLdb as mdb
from ConfigParser import SafeConfigParser


if __name__ == "__main__":

    parser = SafeConfigParser()
    parser.read('config.ini')

    # Connect to the MySQL instance
    db_host = parser.get('log_in', 'host')
    db_name = parser.get('log_in', 'db')
    db_user = parser.get('log_in', 'username')
    db_pass = parser.get('log_in', 'password')

    # con = mdb.connect(
    #     server=db_host, user=db_user, password=db_pass, database=db_name, autocommit=True
    # )

    con = mdb.connect(
        host=db_host, user=db_user, password=db_pass, db=db_name
    )

    # Select all of the historic Google adjusted close data
    sql = """SELECT dp.price_date, dp.adj_close_price
             FROM symbol AS sym
             INNER JOIN daily_price AS dp
             ON dp.symbol_id = sym.id
             WHERE sym.ticker = 'GOOG'
             ORDER BY dp.price_date ASC;"""

    # Create a pandas dataframe from the SQL query
    goog = pd.read_sql_query(sql, con=con, index_col='price_date')    

    # Output the dataframe tail
    print(goog.tail())