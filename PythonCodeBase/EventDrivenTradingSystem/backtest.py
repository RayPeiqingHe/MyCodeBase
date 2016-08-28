from __future__ import print_function

import pprint
try:
    import Queue as queue
except ImportError:
    import queue
import time

import matplotlib.pyplot as plt

import matplotlib.dates as mdates


class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
        self, symbol_list, initial_capital,
        heartbeat, start_date, data_handler, 
        execution_handler, portfolio, strategy, order
    ):
        """
        Initialises the backtest.

        Parameters:
        csv_dir - The hard root to the CSV data directory.
        symbol_list - The list of symbol strings.
        intial_capital - The starting capital for the portfolio.
        heartbeat - Backtest "heartbeat" in seconds
        start_date - The start datetime of the strategy.
        data_handler - data handler object to Handles the market data feed.
        execution_handler - (Class) Handles the orders/fills for trades.
        portfolio - (Class) Keeps track of portfolio current and prior positions.
        strategy - (Class) Generates signals based on market data.
        """
        # self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler = data_handler

        # cls means class. Remember class is an object
        # We later call the constructor of the class to create objects
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.order_cls = order

        # Create Queue to store the events
        # The reason that we are using a Queue is to
        # make sure event is extracted FIFO
        self.events = queue.Queue()
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
       
        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from 
        their class types.
        """
        print(
            "Creating DataHandler, Strategy, Portfolio and ExecutionHandler"
        )

        self.start_date = self.data_handler.start_dt

        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, 
                                            self.order_cls(), self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.data_handler, self.events)

    def _run_backtest(self):
        """
        Executes the backtest.
        """
        i = 0
        while True:
            i += 1
            # print(i)
            # Update the market bars
            if self.data_handler.continue_backtest:
                self.data_handler.update_bars(self.events)
            else:
                break

            # Handle the events
            # Notice that the market event is generated outside of this loop
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    # This is actually the true exit point, when
                    # the event queue becomes empty
                    break
                else:
                    if event is not None:
                        # This if block should be only executed once
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            # Insert new entry for position and holding
                            self.portfolio.update_timeindex(event)

                        # Each signal event corresponds to one symbol
                        # All Signal events must be process before moving on
                        # to the order events
                        elif event.type == 'SIGNAL':
                            self.signals += 1                            
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        self.portfolio.create_equity_curve_dataframe()
        
        print("Creating summary stats...")
        stats = self.portfolio.output_summary_stats()

        pprint.pprint(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

        stats2 = self.portfolio.output_summary_stats2()

        stats2.display()

    def output_plot(self):
        self._output_plot(self.portfolio.equity_curve)

    def _output_plot(self, df_performance):
        """
        Plotting the Equity curve, return, and drawdown

        parameter : Data Frame
            The equity curve from portfolio object
        """

        my_styles = ['b', 'k', 'r']

        cols = ['equity_curve', 'returns', 'drawdown']

        label = ['Portfolio Value %', 'Period Return. %', 'drawdown. %']

        axes = df_performance[cols].plot(subplots=True,
                                         figsize=(8, 6), grid=True, style=my_styles, sharex=False)

        for idx, ax in enumerate(axes):
            ax.set_ylabel(label[idx])

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

            ax.xaxis.set_major_locator(mdates.YearLocator())

        plt.show()

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()
