import bt
import ffn

# fetch some data
data = bt.get('spy,agg', start='2010-01-01')
print data.head()

s = bt.Strategy('s1', [bt.algos.RunMonthly(),
                       bt.algos.SelectAll(),
                       bt.algos.WeighEqually(),
                       bt.algos.Rebalance()])

# create a backtest and run it
test = bt.Backtest(s, data)
res = bt.run(test)


res.plot()

res.display()

res.plot_weights()

#print test.security_weights.tail(20)

#print test.weights.tail(20)

#print test.positions.tail(20)


prices = ffn.get('aapl,msft', start='2010-01-01')


print type(prices)

