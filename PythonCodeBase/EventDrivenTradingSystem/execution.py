from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
try:
    import Queue as queue
except ImportError:
    import queue

from event import FillEvent, OrderEvent

from math import ceil


class ExecutionHandler(object):
    """
    The ExecutionHandler abstract class handles the interaction
    between a set of order objects generated by a Portfolio and
    the ultimate set of Fill objects that actually occur in the
    market. 

    The handlers can be used to subclass simulated brokerages
    or live brokerages, with identical interfaces. This allows
    strategies to be backtested in a very similar manner to the
    live trading engine.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        """
        Takes an Order event and executes it, producing
        a Fill event that gets placed onto the Events queue.

        Parameters:
        event - Contains an Event object with order information.
        """
        raise NotImplementedError("Should implement execute_order()")


class SimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """
    
    def __init__(self, bars, events):
        """
        Initialises the handler, setting the event queues
        up internally.

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Queue of Event objects.
        """
        self.events = events
        self.bars = bars

    def execute_order(self, event):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            fill_event = FillEvent(
                datetime.datetime.utcnow(), event.symbol,
                'ARCA', event.quantity, event.direction, None
            )
            self.events.put(fill_event)


class SimulatedExecutionHandlerWithCommision(ExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.

    But this execution will take into account of commision
    """

    def __init__(self, bars, events):
        """
        Initialises the handler, setting the event queues
        up internally.

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Queue of Event objects.
        """
        self.events = events
        self.bars = bars

    def execute_order(self, event):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            fill_event = FillEvent(
                datetime.datetime.utcnow(), event.symbol,
                'ARCA', event.quantity, event.direction, None
            )

            unit_cost = self.bars.get_latest_bar_value(
            event.symbol, "adj_close")

            if event.direction == 'BUY':
                total_cost = fill_event.calculate_ib_commission() + event.quantity * unit_cost
                max_capital = event.max_capital
            else:
                total_cost = fill_event.calculate_ib_commission()
                max_capital = event.quantity * unit_cost + event.max_capital

            if max_capital < total_cost:
                fill_event.quantity -= ceil((total_cost - event.max_capital) / unit_cost)

            self.events.put(fill_event)


