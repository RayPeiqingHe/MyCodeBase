from __future__ import print_function

try:
    import Queue as queue
except ImportError:
    import queue

import pandas as pd

from event import FillEvent, OrderEvent
from performance import create_sharpe_ratio, create_drawdowns, create_cagr, calc_stats
from order import BaseOrder


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.

    The positions DataFrame stores a time-index of the
    quantity of positions held.

    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular
    time-index, as well as the percentage change in
    portfolio total across bars.
    """

    def __init__(self, bars, events, start_date, order_method, initial_capital=100000.0):
        """
        Initialises the portfolio with bars and an event queue.
        Also includes a starting datetime index and initial capital
        (USD unless otherwise stated).

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.order_method = order_method

        # It is a list of dictionary
        self.all_positions = self.construct_all_positions()

        # Keep track of the most recent position
        self.current_positions = dict([(s, 0) for s in self.symbol_list])

        # It is a list of dictionary
        self.all_holdings = self.construct_all_holdings()

        self.current_holdings = self.construct_current_holdings()

        self.summary_stats = None

        self.position_curve = None

        self.position_history = None

        self.equity_curve = None

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """

        d = dict([(s, 0) for s in self.symbol_list])
        d['datetime'] = self.start_date

        # Notice that it returns a list of dictionary
        # We will keep appending new dictionary as new data comes in
        # It basically contains the position history
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict([(s, 0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital

        # Notice that it returns a list of dictionary
        # We will keep appending new dictionary as new data comes in
        # It basically contains the holding history
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        d = dict([(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital

        # It is a single dictionary as it only stores the most recent data
        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])

        if latest_datetime.strftime("%Y-%m-%d") == '2016-07-06':
            pass

        # Update positions
        # ================

        if self.start_date == latest_datetime:
            dp = self.all_positions[0]
        else:
            dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])

            # Append the current positions
            self.all_positions.append(dp)

        dp['datetime'] = latest_datetime

        # Notice that we simply copy the current position over
        # regardless if it has changes. We do this to keep
        # in sych with the holding
        for s in self.symbol_list:
            dp[s] = self.current_positions[s]

        # Update holdings
        # ===============
        if self.start_date == latest_datetime:
            dh = self.all_holdings[0]
        else:
            dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])

            # Append the current holdings
            self.all_holdings.append(dh)

        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * \
                self.bars.get_latest_bar_value(s, "adj_close")
            dh[s] = market_value
            dh['total'] += market_value

    # ======================
    # FILL/POSITION HANDLING
    # ======================

    def update_positions_from_fill(self, fill):
        """
        Takes a Fill object and updates the position matrix to
        reflect the new position.

        We only update the current positionn here, which will be
        copied over in the update_timeindex method

        Parameters:
        fill - The Fill event object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir*fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to
        reflect the holdings value.

        Parameters:
        fill - The Fill object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(
            fill.symbol, "adj_close"
        )
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        mkt_quantity = 100
        order_type = 'MKT'

        order = self.generate_order_core(signal, mkt_quantity, order_type)

        return order

    def generate_order_core(self, signal, mkt_quantity, order_type='MKT'):
        """
        Central logic to generate order for execution

        Parameters:
        signal - The tuple containing Signal information.
        """

        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        # strength = signal.strength

        cur_quantity = self.current_positions[symbol]

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':

            self.order_method.generate_order(event, self.events, self)

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """

        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

        position_history = pd.DataFrame(self.all_positions)
        position_history.set_index('datetime', inplace=True)
        self.position_history = position_history

    def create_position_dataframe(self):
        """
        Creates a pandas DataFrame from the all positions
        list of dictionaries.
        """

        pos = pd.DataFrame(self.all_positions)
        self.position_curve = pos

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        cagr = create_cagr(total_return, returns)

        stats = [("Total Return", "%0.4f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.4f" % sharpe_ratio),
                 ("CAGR", "%0.4f" % cagr),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        self.summary_stats = {"Total Return": (total_return - 1.0) * 100.0,
                              "Sharpe Ratio": sharpe_ratio,
                              "Max Drawdown": max_dd * 100.0}

        self.equity_curve.to_csv('equity.csv')
        self.position_history.to_csv('position.csv')
        return stats

    def output_summary_stats2(self):
        stats = calc_stats(self.equity_curve[['total']])

        return stats
