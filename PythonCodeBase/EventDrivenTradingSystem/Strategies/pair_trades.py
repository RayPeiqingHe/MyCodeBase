import pandas as pd
import numpy as np

from Strategies.strategy import *


class PairTrades(Strategy):
    """
    Pair trading Strategy with mean revert series
    """

    __metaclass__ = StrategyMetaClass

    def __init__(self, bars, events, look_back,
                 z_entry_threshold=2.0, z_exit_threshold=1.0):
        """
        Initialize the Pair Trading Strategy

        :param bars: The Data handler object
        :param events: The event queue
        :param look_back: the look_back period for hedge ratio
        :return:
        """

        self.bars = bars
        self.events = events
        self.look_back = look_back
        self.y_symbol = self.bars.symbol_list[0]
        self.x_symbol = self.bars.symbol_list[1]
        self.z_entry_threshold = z_entry_threshold
        self.z_exit_threshold = z_exit_threshold

        self.long_market = False
        self.short_market = False

        # dat = pd.DataFrame(range(10))

        # cov = dat.cov()

    def _calculate_xy_signal(self, event):
        pass

    def calculate_signals(self, event):
        """
        generate pair trading signal

        :param event:
        :return:
        """

        if event.type == 'MARKET' \
                and self.bars.get_current_bar_total_number(self.y_symbol) > self.look_back \
                and self.bars.get_current_bar_total_number(self.x_symbol) > self.look_back:
            y_bars = self.bars.get_latest_bars_values(
                self.y_symbol, "adj_close", N=self.look_back)

            x_bars = self.bars.get_latest_bars_values(
                self.x_symbol, "adj_close", N=self.look_back)

            # Use the pandas Ordinary Least Squares method to fit a rolling
            # linear regression between the two closing price time series
            model = pd.ols(y=y_bars, x=x_bars)

            # Construct the hedge ratio and eliminate the first
            # lookback-length empty/NaN period
            hedge_ratio = model.beta['x']

            # Create the spread and then a z-score of the spread
            spread = y_bars - hedge_ratio*x_bars
            zscore = (spread - np.mean(spread))/np.std(spread)

            print(zscore)
