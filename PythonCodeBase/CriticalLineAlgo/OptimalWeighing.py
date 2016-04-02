__author__ = 'Ray'

from numpy import *

# Marginal portfolio cutoff
muc = 0.0001

def standard_optimizer(rt,e,C,lb,ub,x0):
    """
    determines solution to a standard optimization problem.
    All variables with dimensions are of types Numpy Matrix

    :param rt: Investor risk tolerance
    :param e: {n*1} vector of asset expected returns
    :param C: {n*n} return covariance matrix
    :param lb: {n*1} vector of asset lower bounds
    :param ub: {n*1} vector of asset upper bounds
    :param x0: {n*1} vector of initial feasible asset mix
    :return:
    """

    x = x0.copy()

    n = x.size

    while True:
        # The index of the asset to be bought
        ibuy = -1

        # The index of the asset to be sold
        isell = -1

        # Compute the marginal  utility
        mu = e - (1/rt)* 2. * C * x

        # From the marginal  utility, find out the best assets to swap
        for i in range(0, n):
            if ibuy ==  -1 or mu.item((i,0)) > mu.item((ibuy,0)):
                ibuy = i

            if isell == -1 or mu.item((i,0)) < mu.item((isell,0)):
                isell = i

        # Both isell and ibuy need to have values
        if ibuy == -1 or isell == -1 or ibuy == isell:
            break

        tmp = zeros(n)

        tmp[ibuy] = 1.
        tmp[isell] = -1.

        # The asset switch vector
        s = matrix(tmp).T

        k0 = (s.T * e - 2. / rt * s.T * C * x).item(0, 0)
        k1 = (1. / rt * s.T * C * s).item(0, 0)

        # The optimal fraction to swap
        a = k0 / 2. / k1

        buy = x.item((ibuy, 0))
        sell = x.item((isell, 0))

        buy = max(min(a, ub.item((ibuy, 0)) - buy),  0.)

        sell = max(min(a, sell - lb.item((isell, 0))),0.)

        if buy == 0 or sell == 0:
            break;

        tran = min(buy, sell)

        x_tran = matrix(zeros(n)).T
        x_tran[ibuy, 0] = tran
        x_tran[isell, 0] = tran * -1.

        x = x + x_tran

        # Compute the change of utility
        cu = a * k0 - a ** 2 * k1

        if cu <= muc:
            break;

    return x

def main():
    rt = 50.

    x0 = matrix('1.;0.;0.')

    e = matrix('2.80;6.30;10.80')

    std = matrix('1.;7.4;15.4')

    cc = matrix('1.00 0.40 0.15;0.40 1.00 0.35;0.15 0.35 1.00')

    lbd = matrix('0.;0.;0.')

    ubd = matrix('1.;1.;1.')

    C = matrix(diag(std.A1)) * cc * matrix(diag(std.A1))

    w = standard_optimizer(rt, e, C, lbd, ubd, x0)

    print w


if __name__ == '__main__':
    main()

