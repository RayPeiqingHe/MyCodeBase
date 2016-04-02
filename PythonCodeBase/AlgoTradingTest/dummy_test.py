__author__ = 'Ray'

import bt
import backtest2 as bt2
import pandas as pd

dates = pd.date_range('20150701', periods=5)

dict = {'A' : [1, 2, 3, 4, 5], 'B': [1, 2, 1, 2, 1]}

prices = pd.DataFrame(dict, index=dates)

#print prices

# Initialize weights
weights = prices.copy()
weights.iloc[:,:] = 0.5

# Initialize signals
dict2 = {'A' : [False, True, True, False, False], 'B': [False, False, True, False, True]}
signals = pd.DataFrame(dict2, index=dates)

# first we create the Strategy
s = bt.Strategy('summy', [bt.algos.SelectWhere(signals),
                               bt.algos.WeighTarget(weights),
                               bt.algos.Rebalance()])

# now we create the Backtest
t = bt.Backtest(s, prices, commissions=(lambda p, q : 0))

res = bt.run(t)

print t.strategy.data

print pd.concat([t.strategy.positions, prices], axis=1)
