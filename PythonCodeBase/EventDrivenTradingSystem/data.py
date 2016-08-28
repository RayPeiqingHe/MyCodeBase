#!/usr/bin/python
# -*- coding: utf-8 -*-
# data.py
from __future__ import print_function
from abc import ABCMeta, abstractmethod
import os, os.path
import numpy as np
import pandas as pd
from event import MarketEvent
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

    def _get_latest_symbol_data(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            return self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        bars_list = self._get_latest_symbol_data(symbol)

        return bars_list[-1]

    def get_current_bar_total_number(self, symbol):
        """
        Return the total number of bars that has been processed

        :param symbol:
        :return:
        """
        try:
            len(self.latest_symbol_data[symbol].index)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise

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
        bars_list = self._get_latest_symbol_data(symbol)

        return bars_list[-1][0]

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        bars_list = self._get_latest_symbol_data(symbol)

        return getattr(bars_list[-1][1], val_type)

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.

        val_type: the data field name, for instances, adj_close
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            # Notice DataFrame.iterrows returns a collection of tuples
            return np.array([getattr(b[1], val_type) for b in bars_list])

    @abstractmethod
    def update_bars(self, events):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.self.latest_symbol_data
        """
        for s in self.symbol_list:
            try:
                bar = next(self.symbol_data[s])
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)

        # Market event is for all symbol. It basically notifies
        # the system that latest market data is in
        if self.continue_backtest:
            events.put(MarketEvent())

class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """
    def __init__(self, csv_dir, symbol_list):
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
        #self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.symbol_data = {}
        # a dictionary of list
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
        return super(HistoricCSVDataHandler, self).get_latest_bar(symbol)

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        return super(HistoricCSVDataHandler, self).get_latest_bars(symbol, N)

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        return super(HistoricCSVDataHandler, self).get_latest_bar_datetime(symbol)

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        return super(HistoricCSVDataHandler, self).get_latest_bar_value(symbol, val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        return super(HistoricCSVDataHandler, self).get_latest_bars_values(symbol, val_type, N)

    def update_bars(self, events):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        super(HistoricCSVDataHandler, self).update_bars(events)


class SecurityMasterDataHandler(DataHandler):
    """
    SecurityMasterDataHandler is designed to read data for
    each requested symbol from MS SQL and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """
    def __init__(self, symbol_list, sql_conn):
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
        #self.events = events

        # Obtain a database connection to the MySQL instance
        # Connect to the MySQL instance
        parser = SafeConfigParser()
        parser.read('config.ini')
        self.db_query = parser.get('log_in', 'security_master_query')

        self.symbol_list = symbol_list
        self.symbol_data = {}
        # It is a dictionary of string and list
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self._read_sql_datta(sql_conn)


    def _read_sql_datta(self, sql_conn):
        """
        Opens the SQL connection using the given credential, converting
        them into pandas DataFrames within a symbol dictionary.
        For this handler it will be assumed that the data is
        taken from Yahoo. Thus its format will be respected.

        parameters
        ==========
        sql_conn_cls: subclass of SqlConnWrapper
            we will use it to instantiate the object to connnect to sql
        """
        comb_index = None
        self.start_dt = None

        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date

            with sql_conn:
                sql_query = self.db_query % s

                df = sql_conn.execute_query_as_df(sql_query)

                df.set_index('datetime', inplace=True)

                df.sort_index(inplace=True)

                df.index = pd.to_datetime(df.index)

                self.symbol_data[s] = df

            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

            # Since each symbols may have a different starting date for data
            # use the largest one as the global starting date so that
            # all symbols have data on the starting date
            if self.start_dt is None:
                self.start_dt = self.symbol_data[s].index[0].to_datetime()
            else:
                tmp = self.symbol_data[s].index[0].to_datetime()

                if tmp > self.start_dt:
                    self.start_dt = tmp

        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].\
            reindex(index=comb_index, method='pad')

            # Add returns column
            self.symbol_data[s]['returns'] = self.symbol_data[s]['adj_close'].pct_change()*100.0

            self.symbol_data[s] = self.symbol_data[s].loc[self.symbol_data[s].index >= self.start_dt].iterrows()

        # Now self.symbol_data contains the A generator that iterates over the rows of the frame

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        return super(SecurityMasterDataHandler, self).get_latest_bar(symbol)

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        return super(SecurityMasterDataHandler, self).get_latest_bars(symbol, N)

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        return super(SecurityMasterDataHandler, self).get_latest_bar_datetime(symbol)

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        return super(SecurityMasterDataHandler, self).get_latest_bar_value(symbol, val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        return super(SecurityMasterDataHandler, self).get_latest_bars_values(symbol, val_type, N)

    def update_bars(self, events):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        super(SecurityMasterDataHandler, self).update_bars(events)