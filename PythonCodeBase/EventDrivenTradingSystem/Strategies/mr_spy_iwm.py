# mr_spy_iwm.py

import matplotlib.pyplot as plt
import numpy as np
import os
import os.path
import pandas as pd
from ConfigParser import SafeConfigParser
import pymssql as mdb
from performance import create_sharpe_ratio, create_drawdowns


def pull_data_from_sql(symbols):
    curr_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(curr_path, 'config.ini')

    parser = SafeConfigParser()
    parser.read(config_file)

    # Connect to the MySQL instance
    db_host = parser.get('log_in', 'host')
    db_name = parser.get('log_in', 'db')
    db_user = parser.get('log_in', 'username')
    db_pass = parser.get('log_in', 'password')
    db_query = parser.get('log_in', 'security_master_query')

    result = []

    for s in symbols:
        # Load the CSV file with no header information, indexed on date
        cnxn = mdb.connect(
            server=db_host, user=db_user,
            password=db_pass, database=db_name, autocommit=True)

        sql_query = db_query % s

        with cnxn:
            df = pd.read_sql(sql=sql_query, con=cnxn, index_col='datetime', parse_dates=True)

            result.append(df)

    return result


def create_pairs_dataframe(datadir, symbols):
    """Creates a pandas DataFrame containing the closing price
    of a pair of symbols based on CSV files containing a datetime
    stamp and OHLCV data."""

    # Open the individual CSV files and read into pandas DataFrames
    print "Importing CSV data..."

    '''
    sym1 = pd.io.parsers.read_csv(os.path.join(datadir, '%s.csv' % symbols[0]),
                                  header=0, index_col=0,
                                  names=['datetime','open','high','low','close','volume','na'])
    sym2 = pd.io.parsers.read_csv(os.path.join(datadir, '%s.csv' % symbols[1]),
                                  header=0, index_col=0,
                                  names=['datetime','open','high','low','close','volume','na'])
    '''

    result = pull_data_from_sql(symbols)
    sym1 = result[0]
    sym2 = result[1]

    # Create a pandas DataFrame with the close prices of each symbol
    # correctly aligned and dropping missing entries
    print "Constructing dual matrix for %s and %s..." % symbols
    pairs = pd.DataFrame(index=sym1.index)
    pairs['%s_close' % symbols[0].lower()] = sym1['adj_close']
    pairs['%s_close' % symbols[1].lower()] = sym2['adj_close']
    pairs = pairs.dropna()
    return pairs


def calculate_spread_zscore(pairs, symbols, lookback=100):
    """Creates a hedge ratio between the two symbols by calculating
    a rolling linear regression with a defined lookback period. This
    is then used to create a z-score of the 'spread' between the two
    symbols based on a linear combination of the two."""

    # Use the pandas Ordinary Least Squares method to fit a rolling
    # linear regression between the two closing price time series
    print "Fitting the rolling Linear Regression..."
    model = pd.ols(y=pairs['%s_close' % symbols[0].lower()],
                   x=pairs['%s_close' % symbols[1].lower()],
                   window=lookback)

    # Construct the hedge ratio and eliminate the first
    # lookback-length empty/NaN period
    pairs['hedge_ratio'] = model.beta['x']
    pairs = pairs.dropna().copy()

    # Create the spread and then a z-score of the spread
    print "Creating the spread/zscore columns..."
    pairs['spread'] = pairs['spy_close'] - pairs['hedge_ratio']*pairs['iwm_close']
    pairs['zscore'] = (pairs['spread'] - np.mean(pairs['spread']))/np.std(pairs['spread'])
    return pairs


def create_long_short_market_signals(pairs, symbols,
                                     z_entry_threshold=2.0,
                                     z_exit_threshold=1.0):
    """Create the entry/exit signals based on the exceeding of
    z_enter_threshold for entering a position and falling below
    z_exit_threshold for exiting a position."""

    # Calculate when to be long, short and when to exit
    pairs['longs'] = (pairs['zscore'] <= -z_entry_threshold)*1.0
    pairs['shorts'] = (pairs['zscore'] >= z_entry_threshold)*1.0
    pairs['exits'] = (np.abs(pairs['zscore']) <= z_exit_threshold)*1.0

    # These signals are needed because we need to propagate a
    # position forward, i.e. we need to stay long if the zscore
    # threshold is less than z_entry_threshold by still greater
    # than z_exit_threshold, and vice versa for shorts.
    pairs['long_market'] = 0.0
    pairs['short_market'] = 0.0

    # These variables track whether to be long or short while
    # iterating through the bars
    long_market = 0
    short_market = 0

    # Calculates when to actually be "in" the market, i.e. to have a
    # long or short position, as well as when not to be.
    # Since this is using iterrows to loop over a dataframe, it will
    # be significantly less efficient than a vectorised operation,
    # i.e. slow!
    print "Calculating when to be in the market (long and short)..."
    for i, b in enumerate(pairs.iterrows()):
        # Calculate longs
        if b[1]['longs'] == 1.0:
            long_market = 1
        # Calculate shorts
        if b[1]['shorts'] == 1.0:
            short_market = 1
        # Calculate exists
        if b[1]['exits'] == 1.0:
            long_market = 0
            short_market = 0
        # This directly assigns a 1 or 0 to the long_market/short_market
        # columns, such that the strategy knows when to actually stay in!
        pairs.ix[i]['long_market'] = long_market
        pairs.ix[i]['short_market'] = short_market
    return pairs


def create_portfolio_returns(pairs, symbols):
    """Creates a portfolio pandas DataFrame which keeps track of
    the account equity and ultimately generates an equity curve.
    This can be used to generate drawdown and risk/reward ratios."""

    # Convenience variables for symbols
    sym1 = symbols[0].lower()
    sym2 = symbols[1].lower()

    # Construct the portfolio object with positions information
    # Note that minuses to keep track of shorts!
    print "Constructing a portfolio..."
    portfolio = pd.DataFrame(index=pairs.index)
    portfolio['positions'] = pairs['long_market'] - pairs['short_market']
    portfolio[sym1] = -1.0 * pairs['%s_close' % sym1] * portfolio['positions']
    portfolio[sym2] = pairs['%s_close' % sym2] * portfolio['positions']
    portfolio['total'] = portfolio[sym1] + portfolio[sym2]

    # Construct a percentage returns stream and eliminate all
    # of the NaN and -inf/+inf cells
    print "Constructing the equity curve..."
    portfolio['returns'] = portfolio['total'].pct_change()
    portfolio['returns'].fillna(0.0, inplace=True)
    portfolio['returns'].replace([np.inf, -np.inf], 0.0, inplace=True)
    portfolio['returns'].replace(-1.0, 0.0, inplace=True)

    # Calculate the full equity curve
    portfolio['cum_returns'] = (portfolio['returns'] + 1.0).cumprod()
    return portfolio


if __name__ == "__main__":
    datadir = '/your/path/to/data/'  # Change this to reflect your data path!
    symbols = ('SPY', 'IWM')

    # lookbacks = range(50, 210, 10)

    lookbacks = range(21, 126, 10)

    returns = []

    sharps = []

    draw_downs = []

    periods = 252

    # Adjust lookback period from 50 to 200 in increments
    # of 10 in order to produce sensitivities
    for lb in lookbacks:
        print "Calculating lookback=%s..." % lb
        pairs = create_pairs_dataframe(datadir, symbols)
        pairs = calculate_spread_zscore(pairs, symbols, lookback=lb)
        pairs = create_long_short_market_signals(pairs, symbols,
                                                 z_entry_threshold=2.0,
                                                 z_exit_threshold=1.0)

        portfolio = create_portfolio_returns(pairs, symbols)
        returns.append(portfolio.ix[-1]['cum_returns'])
        sharps.append(create_sharpe_ratio(portfolio['returns']))
        drawdown, max_dd, dd_duration = create_drawdowns(portfolio['cum_returns'])
        draw_downs.append(max_dd)

    df = pd.DataFrame(lookbacks)
    df.columns = ['LookBack']
    df['Returns'] = returns
    df['Sharps'] = sharps
    df['Max Draw Down'] = draw_downs

    print df

    print "Plot the lookback-performance scatterchart..."
    plt.plot(lookbacks, returns, '-o')
    plt.show()
