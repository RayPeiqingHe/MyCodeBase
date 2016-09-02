#!/usr/bin/python
# -*- coding: utf-8 -*-

# snp_forecast.py

from __future__ import print_function

import pandas as pd
# from sklearn.qda import QDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

from Strategies.strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from execution import *
from portfolio import Portfolio
from create_lagged_series import create_lagged_series
from data import SecurityMasterDataHandler
from order import *


class SPYDailyForecastStrategy(Strategy):
    """
    S&P500 forecast strategy. It uses a Quadratic Discriminant
    Analyser to predict the returns for a subsequent time
    period and then generated long/exit signals based on the
    prediction.
    """
    def __init__(self, bars, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.datetime_now = datetime.datetime.utcnow()

        self.model_start_date = datetime.datetime(2001, 1, 10)
        self.model_end_date = datetime.datetime(2005, 12, 31)
        self.model_start_test_date = datetime.datetime(2005, 1, 1)

        self.long_market = False
        self.short_market = False
        self.bar_index = 0

        self.model = self.create_symbol_forecast_model()

    def create_symbol_forecast_model(self):
        # Create a lagged series of the S&P500 US stock market index
        snpret = create_lagged_series(
            self.symbol_list[0], self.model_start_date,
            self.model_end_date, lags=5
        )

        # Use the prior two days of returns as predictor
        # values, with direction as the response
        x = snpret[["Lag1", "Lag2"]]
        y = snpret["Direction"]

        # Create training and test sets, each of them is series
        start_test = self.model_start_test_date
        x_train = x[x.index < start_test]
        x_test = x[x.index >= start_test]
        y_train = y[y.index < start_test]
        y_test = y[y.index >= start_test]

        model = QuadraticDiscriminantAnalysis()
        model.fit(x_train, y_train)

        # return nd array
        pred_test = model.predict(x_test)

        print("Error Rate is {0}".format((y_test != pred_test).sum() * 1. / len(y_test)))

        return model

    def calculate_signals(self, event):
        """
        Calculate the SignalEvents based on market data.
        """
        sym = self.symbol_list[0]
        dt = self.datetime_now

        if event.type == 'MARKET':
            self.bar_index += 1
            if self.bar_index > 5:
                lags = self.bars.get_latest_bars_values(
                    self.symbol_list[0], "returns", n=3
                )

                # print(lags)

                """ May be bug?
                pred_series = pd.Series(
                    {
                        'Lag1': lags[1]*100.0,
                        'Lag2': lags[2]*100.0
                    }
                )
                """

                pred_series = pd.Series(
                    {
                        'Lag1': lags[2]*100.0,
                        'Lag2': lags[1]*100.0
                    }
                )

                bar_date = self.bars.get_latest_bar_datetime(sym)

                pred = self.model.predict(pred_series.reshape(1, -1))

                """
                print(pred_series)

                print("Reshape series")

                print(pred_series.reshape(1, -1))

                print ('Raw series date {0} pred: {1}'.format(bar_date, pred))

                print("done")
                """

                if pred > 0 and not self.long_market:
                    self.long_market = True
                    # print('LONG: {0} {1}'.format(bar_date, sym))
                    signal = SignalEvent(1, [sym], dt, 'LONG', 1.0)
                    self.events.put(signal)

                if pred < 0 and self.long_market:
                    self.long_market = False
                    # print('SHORT: {0} {1}'.format(bar_date, sym))
                    signal = SignalEvent(1, [sym], dt, 'EXIT', 1.0)
                    self.events.put(signal)


if __name__ == "__main__":

    import sys

    if '../SqlConnWraper' not in sys.path:
        sys.path.append('../SqlConnWraper')

    from BuildSQLConnection import build_sql_conn

    cxcn = build_sql_conn('config.ini', '../SqlConnWraper/data/spy.csv')

    symbol_list = ['SPY']
    initial_capital = 100000.0
    heartbeat = 0.0

    # The returns columns is computed in data handler
    data_handler = SecurityMasterDataHandler(symbol_list, cxcn)

    start_date = data_handler.start_dt

    order_method = EquityWeightOrder
    order_method = NaiveOrder

    backtest = Backtest(
        symbol_list, initial_capital, heartbeat,
        start_date, data_handler, SimulatedExecutionHandlerWithCommision,
        Portfolio, SPYDailyForecastStrategy, order_method
    )

    backtest.simulate_trading()

    backtest.output_plot()
