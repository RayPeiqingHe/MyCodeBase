__author__ = 'Ray'

import numpy as np

from scipy import optimize


class MarketRateCalibrator(object):
    """
    Class that performs optimization using scipy.optimize
    """
    def __init__(self, lambdas, tvec, rc, x0, *mkt_rate_objs):
        """
        Constructor of the class
        :param lambdas: The list of lambda used in Tikhonov regularizer
        :param tvec: the knots point array
        :param rc: The rate calculator
        :param x0: Initial guess
        """
        self._lambdas = lambdas

        #The knot points time array
        self._tvec = tvec

        #n is the number of knot points
        self._n = len(tvec)
        self._rc = rc
        self._x0 = x0

        self._mkt_rate_objs = mkt_rate_objs

        self.T0 = 0
        self.T_max = 30

    def optimize(self, *fitobjs):
        """
        Perform optimization using scipy.optimize

        :param fitobjs: The array of market rate objects to be used
                        in the optimizer
        :return:
        """

        factr = 1e-7

        """Objective function"""
        def f(x):
            error = 0.0
            for item in  self._mkt_rate_objs:
                error += self.square_error(item.calibrate(x[:self._n], x[self._n:]), item.act())
            pnty = self._rc.Tikhonov_regularizer(x[:self._n], x[self._n:], self._lambdas, self.T0, self.T_max)
            #pnty = self._rc.Tikhonov_regularizer(x[:self._n], x[self._n:], self._lambdas)

            return error + pnty

        res = optimize.minimize(f, self._x0, method='BFGS', options={'disp': True, 'gtol': factr})

        xopt = res.x
        fmin = factr

        print "fmin = ", fmin
        return xopt


    def square_error(self, x, y):
        """
        Function to return the square error
        :param x: input array of x
        :param y: input array of y
        :return: the square error
        """
        return sum((np.asarray(x) - np.asarray(y))**2)

