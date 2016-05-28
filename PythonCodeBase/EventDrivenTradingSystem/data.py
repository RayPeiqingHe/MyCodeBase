#!/usr/bin/python
# -*- coding: utf-8 -*-
# data.py
from __future__ import print_function
from abc import ABCMeta, abstractmethod
import datetime
import os, os.path
import numpy as np
import pandas as pd
from event import MarketEvent
import pymssql as mdb
from ConfigParser import SafeConfigParser


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).
    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OHLCVI) for each symbol requested.
    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed.
        """
        for b in self.symbol_data[symbol]:
            yield b

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
           return bars_list[-1]

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())


class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """
    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.
        It will be assumed that all files are of the form
        ’symbol.csv’, where symbol is a string in the list.
        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self._open_convert_csv_files()


    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.
        For this handler it will be assumed that the data is
        taken from Yahoo. Thus its format will be respected.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0, index_col=0, parse_dates=True,
                names=[
                'datetime', 'open', 'high',
                'low', 'close', 'volume', 'adj_close'
                ]
                ).sort()

        # Combine the index to pad forward values
        if comb_index is None:
            comb_index = self.symbol_data[s].index
        else:
            comb_index.union(self.symbol_data[s].index)
        # Set the latest symbol_data to None
        self.latest_symbol_data[s] = []
        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].\
            reindex(index=comb_index, method='pad').iterrows()

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        super(HistoricCSVDataHandler, self).get_latest_bar(symbol)

    def _get_new_bar(self, symbol):
        super(HistoricCSVDataHandler, self)._get_new_bar(symbol)

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        super(HistoricCSVDataHandler, self).get_latest_bars(symbol, N)

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        super(HistoricCSVDataHandler, self).get_latest_bar_datetime(symbol)

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        super(HistoricCSVDataHandler, self).get_latest_bar_value(symbol, val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        super(HistoricCSVDataHandler, self).get_latest_bars_values(symbol, val_type, N)

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        super(HistoricCSVDataHandler, self).update_bars()


class SecurityMasterDataHandler(DataHandler):
    """
    SecurityMasterDataHandler is designed to read data for
    each requested symbol from MS SQL and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """
    def __init__(self, events, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.
        It will be assumed that all files are of the form
        ’symbol.csv’, where symbol is a string in the list.
        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events

        # Obtain a database connection to the MySQL instance
        # Connect to the MySQL instance
        parser = SafeConfigParser()
        parser.read('config.ini')

        # Connect to the MySQL instance
        self.db_host = parser.get('log_in', 'host')
        self.db_name = parser.get('log_in', 'db')
        self.db_user = parser.get('log_in', 'username')
        self.db_pass = parser.get('log_in', 'password')

        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self._read_sql_datta()


    def _read_sql_datta(self):
        """
        Opens the SQL connection using the given credential, converting
        them into pandas DataFrames within a symbol dictionary.
        For this handler it will be assumed that the data is
        taken from Yahoo. Thus its format will be respected.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            cnxn = mdb.connect(
                server=self.db_host, user=self.db_user,
                password=self.db_pass, database=self.db_name, autocommit=True)

            sql_query = "SELECT * from dbo.ufn_historical_price('%s')" % s

            with cnxn:
                df = pd.read_sql(sql=sql_query, con=cnxn, index_col='datetime', parse_dates=True)

        # Combine the index to pad forward values
        if comb_index is None:
            comb_index = self.symbol_data[s].index
        else:
            comb_index.union(self.symbol_data[s].index)
        # Set the latest symbol_data to None
        self.latest_symbol_data[s] = []
        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].\
            reindex(index=comb_index, method='pad').iterrows()

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        super(SecurityMasterDataHandler, self).get_latest_bar(symbol)

    def _get_new_bar(self, symbol):
        super(SecurityMasterDataHandler, self)._get_new_bar(symbol)

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        super(SecurityMasterDataHandler, self).get_latest_bars(symbol, N)

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        super(SecurityMasterDataHandler, self).get_latest_bar_datetime(symbol)

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        super(SecurityMasterDataHandler, self).get_latest_bar_value(symbol, val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        super(SecurityMasterDataHandler, self).get_latest_bars_values(symbol, val_type, N)

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        super(SecurityMasterDataHandler, self).update_bars()