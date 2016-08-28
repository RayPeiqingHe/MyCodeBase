from __future__ import print_function

import unittest
from backtest import Backtest
from data import SecurityMasterDataHandler
from execution import *
from portfolio import Portfolio
from order import *


class StrategiesTest(unittest.TestCase):

    def setUp(self):

        import sys

        if '../../SqlConnWraper' not in sys.path:
            sys.path.append('../../SqlConnWraper')

        if '../Strategies' not in sys.path:
            sys.path.append('../Strategies')

        from BuildSQLConnection import build_sql_conn

        self.cxcn = build_sql_conn('../config.ini')

    def test_mac_strategy(self):
        """
        Unit test for Moving Average Crossover Strategy

        :return:
        """

        from mac import MovingAverageCrossStrategy

        symbol_list = ['AAPL']
        initial_capital = 100000.0
        heartbeat = 0.0

        data_handler = SecurityMasterDataHandler(symbol_list, self.cxcn)

        start_date = data_handler.start_dt

        order_method = EquityWeightOrder

        backtest = Backtest(
            symbol_list, initial_capital, heartbeat,
            start_date, data_handler, SimulatedExecutionHandlerWithCommision,
            Portfolio, MovingAverageCrossStrategy, order_method
        )

        backtest.simulate_trading()

        print(backtest.portfolio.summary_stats)

        self.assertAlmostEqual(backtest.portfolio.summary_stats['Total Return'],
                               -11.908907924000056, places=7, msg=None, delta=None)

        self.assertAlmostEqual(backtest.portfolio.summary_stats['Sharpe Ratio'],
                               0.17652509997281265, places=7, msg=None, delta=None)

        self.assertAlmostEqual(backtest.portfolio.summary_stats['Max Drawdown'],
                               74.337676325221068, places=7, msg=None, delta=None)


if __name__ == '__main__':
    unittest.main()
