from __future__ import print_function

import numpy as np
import pandas as pd
import ffn


def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """

    return np.sqrt(periods) * np.mean(returns) / np.std(returns)


def create_cagr(tot_return, returns, periods=252):
    """
    Computation of CAGR

    Parameters
    ==========
    tot_return: float
    returns: DataFrame
    periods: int
    """

    return pow(tot_return, 1. / ((len(returns) - 1.) / periods)) - 1


def create_drawdowns(pnl):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.
          In this case it is the equity curve

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve 
    # and set up the High Water Mark
    hwm = [0]

    # Create the drawdown and duration series
    idx = pnl.index
    drawdown = pd.Series(index=idx)
    duration = pd.Series(index=idx)

    # Loop over the index range
    for t in range(1, len(idx)):
        hwm.append(max(hwm[t-1], pnl[t]))

        # since hwm only contains the last high water market
        # It garantees hwm[t] >= pnl[t]
        drawdown[t] = (hwm[t]-pnl[t]) / hwm[t]
        # duration[tv]= (0 if drawdown[t] == 0 else duration[t-1]+1)
        duration[t] = (0 if drawdown[t] <= 0 else duration[t-1]+1)

    return drawdown, drawdown.max(), duration.max()


def calc_stats(prices):

    stats = prices.calc_stats()
    return stats
