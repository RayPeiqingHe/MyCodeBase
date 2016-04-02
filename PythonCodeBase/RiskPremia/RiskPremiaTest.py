__author__ = 'Ray'

from numpy import *

price = 1.5

num_of_runs = 100000

invest = array([price] * num_of_runs)

profit = array([0] * num_of_runs)

p = random.uniform(size = num_of_runs)

# Suppose p > 0.5 is head, and we make 2 dollar

profit[p >= 0.5] = 2

ret = profit / invest - 1

print ret.mean()