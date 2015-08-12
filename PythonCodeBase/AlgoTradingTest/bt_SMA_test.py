__author__ = 'Ray'

import bt
import backtest2 as bt2
from matplotlib import pyplot as plt
#%pylab inline
# download data

class SelectWhere(bt.Algo):

    """
    Selects securities based on an indicator DataFrame.

    Selects securities where the value is True on the current date (target.now).

    Args:
        * signal (DataFrame): DataFrame containing the signal (boolean DataFrame)

    Sets:
        * selected

    """
    def __init__(self, signal):
        self.signal = signal

    def __call__(self, target):
        # get signal on target.now
        if target.now in self.signal.index:
            sig = self.signal.ix[target.now]

            # get indices where true as list
            selected = list(sig.index[sig])

            # save in temp - this will be used by the weighing algo
            target.temp['selected'] = selected

        # return True because we want to keep on moving down the stack
        return True

data = bt.get('aapl,msft,c,gs,ge', start='2010-01-01')

# calculate moving average DataFrame using pandas' rolling_mean
import pandas as pd
# a rolling mean is a moving average, right?
sma = pd.rolling_mean(data, 50)

# let's see what the data looks like - this is by no means a pretty chart, but it does the job
tmp = bt.merge(data, sma).asfreq('m', 'ffill').rebase()
plot = tmp.plot(figsize=(15, 5))

signal = data > sma

# first we create the Strategy
s = bt.Strategy('above50sma', [SelectWhere(data > sma),
                               bt.algos.WeighEqually(),
                               bt.algos.Rebalance()])

# now we create the Backtest
t = bt.Backtest(s, data)

# and let's run it!
res = bt2.run(t)

# what does the equity curve look like?
res.plot('d')

res.plot_security_weights()

# and some performance stats
res.display()

plt.show()