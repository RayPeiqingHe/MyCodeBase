__author__ = 'Ray'

from numpy import *
from scipy.stats import *
import matplotlib.pyplot as plt
import math

def norm_pdf(x, mean = 0, sigma = 1):
    return 1 / sqrt(2 * math.pi) / sigma * exp(-1. * (x - mean)**2 / 2 / (sigma ** 2))

x = linspace(-10.0, 10.0, num=100)

sigma = 0.3

r = 0.02

T = 10.

F = 100.

V0 = 95.

V0_s = [95., 99., 120., 140.]

d = norm.pdf(x, 0, sqrt(T))
#d = norm_pdf(x, 0, sqrt(T))

print (d * 0.2).sum()

fig = plt.figure()

ax_s = [fig.add_subplot(221), fig.add_subplot(222), fig.add_subplot(223), fig.add_subplot(224)]

for i in range(0, len(V0_s)):
    V0 = V0_s[i]

    V = V0 * exp(sigma * x + (r - sigma ** 2 / 2) * T)

    LGD = maximum.reduce([1 - V / F, array([0] * 100)])

    cutoff = (log(F / V0) - (r - sigma ** 2 / 2) * T) / sigma

    ax_s[i].plot(LGD, d * LGD)
    ax_s[i].set_title('LGD with V_0 ={0}'.format(V0))
    ax_s[i].set_xlabel('LGD')
    ax_s[i].set_ylabel('density')

    print 'Expected LGD is {0}'.format((d * LGD ).sum())


plt.show()

"""
print norm.cdf(cutoff, 0, sqrt(T))

print (LGD * LGD * d * LGD).sum()

plt.plot(LGD, d * LGD)

plt.show()

"""

"""
z = norm.pdf(x, 0,1)

plt.plot(exp(x), z * exp(x))

plt.show()
"""




