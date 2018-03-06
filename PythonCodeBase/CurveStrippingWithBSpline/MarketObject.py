from __future__ import division, print_function, absolute_import
import numpy as np


class IrSwap(object):

    def __init__(self, spot_date, tenor, discount_curve, forward_rate_curve):
        self.discount_curve = discount_curve

        self.forward_rate_curve = forward_rate_curve

        self.spot_date = spot_date

        self.tenor = tenor

        self.fix_freq = 2

        self.float_freq = 4

    def get_annuity(self, freq=None):
        annuity = 0

        if freq is None:
            freq = self.fix_freq

        for t in xrange(1, int(freq * self.tenor) + 1):
            annuity += 1. / freq * self.discount_curve.discount_factor(self.spot_date, t / freq + self.spot_date)

        return annuity

    def get_floating_leg(self, floaring_rate_curve=None):
        floating_leg = 0

        if floaring_rate_curve is None:
            floaring_rate_curve = self.forward_rate_curve

        for t in xrange(1, int(self.tenor * self.float_freq) + 1):
            floating_leg += 1. / self.float_freq * \
                            floaring_rate_curve.forward_rate((t - 1) / self.float_freq + self.spot_date
                                                             , t / self.float_freq + self.spot_date) * \
                            self.discount_curve.discount_factor(self.spot_date, t / self.float_freq + self.spot_date)

        return floating_leg

    def get_swap_rate(self):
        return self.get_floating_leg() / self.get_annuity()


class BasisSwap(IrSwap):

    def get_basis_spread(self):
        libor_leg = self.get_floating_leg(self.forward_rate_curve)

        ois_leg = self.get_floating_leg(self.discount_curve)

        annuity = self.get_annuity(self.float_freq)

        return (libor_leg - ois_leg) / annuity


class BaseCurve(object):
    """
    class of instatanous curve for discount factor and forward curve
    """

    def __init__(self, b_spline):
        self.b_spline = b_spline

    def __basis_sum(self, s, t):
        integral_sum = self.b_spline.integrate(s, t)

        return integral_sum

    def discount_factor(self, s, t):
        integral_sum = self.__basis_sum(s, t)

        return np.exp(-integral_sum)

    def forward_rate(self, s, t):
        integral_sum = self.__basis_sum(s, t)

        return 1. / (t - s) * (np.exp(integral_sum) - 1)

    def display(self, xpts=None):
        if xpts is None:
            xpts = np.linspace(0, 30, 100)

        func = np.vectorize(self.b_spline.__call__)

        print(xpts)

        print(func(xpts))

    def plot(self, xpts=None):
        import matplotlib.pyplot as plt

        if xpts is None:
            xpts = np.linspace(0, 30, 100)

        func = np.vectorize(self.b_spline.__call__)

        plt.plot(xpts, func(xpts))
