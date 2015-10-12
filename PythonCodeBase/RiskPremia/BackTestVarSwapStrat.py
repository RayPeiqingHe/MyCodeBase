__author__ = 'Ray'

from pandas import *
import numpy as np

num_trading_days_year = 252

def run_back_test(sp_data, varSwap, daysToExp):
    """

    :param sp_data: Data frame of the historical S&P index data
    :param varSwap: The quote of the
    :param daysToExp: The expiry of the variance swap in trading days
    :return:
    """

    varSwap_sub = varSwap[(varSwap['BusinessDays'] == daysToExp)]

    if not ('LogReturns' in sp_data):
        sp_data['LogReturns'] = np.log(sp_data['gspc'] / sp_data.shift(1)['gspc'])

        sp_data['LogReturnsSquare'] = sp_data['LogReturns'] ** 2

    trading_data = sp_data.join(varSwap_sub.shift(daysToExp), how = 'left', lsuffix='_x')

    trading_data['Realized_variance'] = rolling_mean(trading_data['LogReturnsSquare'], daysToExp)

    trading_data['Annualized_Realized_variance'] = trading_data['Realized_variance'] * num_trading_days_year

    trading_data['vsQuote_square'] = trading_data['vsQuote'] ** 2

    trading_data.dropna(inplace=True)

    trading_data['P&L'] = trading_data['vsQuote_square'] - trading_data['Annualized_Realized_variance']

    return trading_data
