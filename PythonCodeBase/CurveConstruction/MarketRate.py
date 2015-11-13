__author__ = 'Ray'

"""
This module models various kinds of market rates
and perform fitting calculation
"""

import numpy as np

class MarketRate(object):
    """
    Base class of market rate input
    """
    def __init__(self, rc):
        self._rc_ = rc

    def act(self):
        """

        :return: the actual values of the corresponding rate
        """
        return self._rvec_


class SwapRate(MarketRate):
    """
    Class for the Swap rate input
    """
    def __init__(self, rc, **kwargs):
        super(SwapRate, self).__init__(rc)

        self._rvec_ = np.asarray(kwargs['rate'])

        self._tenor_ = np.asarray(kwargs['Tenor'])

        self._t0_ = np.asarray(kwargs['Spot_Date'])

    def calibrate(self, f_k, l_k):
        """
        Fitting function to be called in the optimizer
        :param f_k: the coefficients of the OIS rate basis functions
        :param l_k: the coefficients of the Libor rate basis functions
        :return: the calculate swap rates using the fitting data
        """
        fitted = map(lambda t0, tenor: \
            self._rc_.swap_rate(t0, tenor, f_k, l_k), \
                     self._t0_, self._tenor_)
        return np.asarray(fitted)


class BasisSwapRate(MarketRate):
    """
    Class for the Basis Swap rate input
    """
    def __init__(self, rc, **kwargs):
        super(BasisSwapRate, self).__init__(rc)

        self._rvec_ = np.asarray(kwargs['rate'])/10000 # in basis points

        self._tenor_ = np.asarray(kwargs['Tenor'])

        self._t0_ = np.asarray(kwargs['Spot_Date'])

    def calibrate(self, f_k, l_k):
        """
        Fitting function to be called in the optimizer
        :param f_k: the coefficients of the OIS rate basis functions
        :param l_k: the coefficients of the Libor rate basis functions
        :return: the calculate Basis Swap rate using the fitting data
        """
        fitted = map(lambda t0, tenor: \
            self._rc_.basis_swap_rate(t0, tenor, f_k, l_k), \
                     self._t0_, self._tenor_)
        return np.asarray(fitted)

class EuroDollar(MarketRate):
    """
    Class for the Euro Dollar rate input
    """
    def __init__(self, rc, **kwargs):
        super(EuroDollar, self).__init__(rc)

        self._rvec_ = np.asarray(kwargs['rate'])

        self._tvec_ = np.asarray(kwargs['Fixing_Date'])

        self._tenor_ = np.asarray(kwargs['Tenor'])

    def calibrate(self, f_k, l_k):
        """
        Fitting function to be called in the optimizer
        :param f_k: the coefficients of the OIS rate basis functions
        :param l_k: the coefficients of the Libor rate basis functions
        :return: the calculate Euro Dollar forward rate using the fitting data
        """
        fitted = map(lambda t, t2: self._rc_.libor_fwd_rate(t, t + t2, l_k), self._tvec_, self._tenor_)
        return np.asarray(fitted)

class LiborFixing(MarketRate):
    """
    Class for the Libor fixing input
    """
    def __init__(self, rc, **kwargs):
        super(LiborFixing, self).__init__(rc)

        self._rvec_ = np.asarray(kwargs['rate'])

        self._tvec_ = np.asarray(kwargs['Spot_Date'])

    def calibrate(self, f_k, l_k):
        """
        Fitting function to be called in the optimizer
        :param f_k: the coefficients of the OIS rate basis functions
        :param l_k: the coefficients of the Libor rate basis functions
        :return: the calculate Libor fixing rate using the fitting data
        """
        fitted = map(lambda t: self._rc_.inst_libor_fwd_rate(t, l_k), self._tvec_)

        return np.asarray(fitted)


class FedFundRate(MarketRate):
    """
    Class for the Fed Fund rate input
    """
    def __init__(self, rc, **kwargs):
        super(FedFundRate, self).__init__(rc)

        self._rvec_ = np.asarray(kwargs['rate'])

        self._tvec_ = np.asarray(kwargs['Spot_Date'])

    def calibrate(self, f_k, l_k):
        """
        Fitting function to be called in the optimizer
        :param ffr: the coefficients of the OIS rate basis functions
        :param lbr: the coefficients of the Libor rate basis functions
        :return: the calculate Fed fund rate using the fitting data
        """

        fitted = map(lambda t: self._rc_.inst_ois_fwd_rate(t, f_k), self._tvec_)

        return np.asarray(fitted)

