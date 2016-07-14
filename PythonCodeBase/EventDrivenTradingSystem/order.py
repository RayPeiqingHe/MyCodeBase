# order.py

from __future__ import print_function

from abc import ABCMeta, abstractmethod

from event import OrderEvent

from math import floor


class BaseOrder(object):
    """
    The order class is the abstract based class for order generation

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_order(self, signal, events, port):
        """
        Provides the mechanisms to calculate the list of signals.

        signal: the signal event for order generation
        events: the event queue
        port: the portfolio object
        """
        raise NotImplementedError("Should implement calculate_signals()")

    def generate_order_core(self, symbol, direction, strength,
                            mkt_quantity, cur_quantity, order_type = 'MKT'):
        """
        Central logic to generate order for execution

        Parameters:
        signal - The tuple containing Signal information.
        """

        order = None

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')

        return order


class NaiveOrder(BaseOrder):
    """
    naive order: use the fixed quantity of 100
    """

    def generate_order(self, signal, events, port):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        events: the event queue
        port: the portfolio object
        """

        for symbol in signal.symbols:
            mkt_quantity = 100
            order_type = 'MKT'

            cur_quantity = port.current_positions[symbol]

            order = self.generate_order_core(symbol, signal.signal_type, signal.strength,
                                             mkt_quantity, cur_quantity, order_type)

            events.put(order)


class EquityWeightOrder(BaseOrder):
    """
    Equal weighted order based on current total cash

    """

    def generate_order(self, signal, events, port):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        events: the event queue
        port: the portfolio object
        """

        order_type = 'MKT'

        for symbol in signal.symbols:
            allocate_captial = port.current_holdings['cash'] / len(signal.symbols)

            mkt_quantity = floor(allocate_captial / port.bars.get_latest_bar_value(symbol, "adj_close"))

            cur_quantity = port.current_positions[symbol]

            order = self.generate_order_core(symbol, signal.signal_type, signal.strength,
                                             mkt_quantity, cur_quantity, order_type)

            events.put(order)