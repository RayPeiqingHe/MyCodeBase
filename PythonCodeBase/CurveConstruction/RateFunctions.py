__author__ = 'Ray'

from math import exp
from BSpline import *


class Rate_Functions(object):
    def __init__(self, time_vector):
        """
        class for calculating different rates like discount factor and libor forward rates
        There are:

        disc_factor
        libor_fwd_rate
        ois_fwd_rate
        libor_ois_spread
        basis_swap_rate
        inst_ois_fwd_rate
        inst_libor_fwd_rate

        Also calculate PV of Swap

        Params:
        d:degree
        T: time_vector
        B_Spline: object of class B_Spline
        Integral_Lish: Gamma: Prevent multi-calculation for recursion
        """
        self.d = 3
        self.T = np.asarray(time_vector)
        self.B_Spline = B_Spline(self.T)
        self.length = len(self.T) - self.d - 1
        self.Integral_List = {}
        self.b_cross_integral_list = self.b_cross_integral(0, 30)
    def __str__(self):
        return "Calculate different Discount Factor and Libor Rates Based on b Functions"

    def disc_factor(self, S, T, f):
        return exp( np.dot(f[0:self.length], self.integral_list(S,T)))

    def libor_fwd_rate(self, S, T, l):
        if T==S:
            return 0
        return  (exp(np.dot(l[0:self.length], self.integral_list(S,T))) - 1) / (T - S)

    def PV_Swap(self,tenor,fixed_rate,fopt,lopt,N=100,T_0=0):
        day_count_fix = 2
        day_count_float = 4
        annuity = 0.0
        for t in range(1, int(round(day_count_fix * tenor)) + 1):
            annuity += self.disc_factor(0, t, fopt)
        p_float = 0.0
        for t in range(1, int(round(day_count_float * tenor)) + 1):
                p_float += self.libor_fwd_rate( (t - 1) / day_count_float, t / day_count_float, lopt) *  self.disc_factor(0, t / day_count_float, fopt)
        return N*(fixed_rate*annuity-p_float)

    def swap_rate(self, T_0, tenor, f, l):
        annuity = 0
        day_count_fix=2
        day_count_float = 4
        for t in range(1, int(round(day_count_fix * tenor)) + 1):
            annuity += self.disc_factor(0, T_0 + t / day_count_fix, f)
        p_float = 0
        for t in range(1, int(round(day_count_float * tenor)) + 1):
            l_temp = self.libor_fwd_rate( (t - 1) / day_count_float, t / day_count_float, l)
            p_float += l_temp * self.disc_factor(0, T_0 + t / day_count_float, f)
        result = p_float / annuity
        return result

    def ois_fwd_rate(self, S, T, f):
        return self.fwd_rate(S, T, f)

    def libor_ois_spread(self, S, T, f, l):
        return self.libor_fwd_rate(S, T, l) - self.ois_fwd_rate(S, T, f)

    def basis_swap_rate(self, T_0, tenor, f, l):
        part1 = 0
        part2 = 0
        freq = 4
        for t in range(1, int(round(freq * tenor)) + 1):
            l_temp = self.libor_fwd_rate((t - 1)/ freq, t / freq, l)
            f_temp = self.ois_fwd_rate((t - 1) / freq, t / freq, f)
            disc_factor = self.disc_factor(0, T_0 + t / freq, f)
            part1 += (l_temp - f_temp) * disc_factor
            part2 += disc_factor
        return part1 / part2

    def inst_ois_fwd_rate(self, T, f):
        return np.dot(f[0:self.length], self.bf_list(T))

    def inst_libor_fwd_rate(self, T, l):
        return np.dot(l[0:self.length], self.bf_list(T))

    def Tikhonov_regularizer(self, f, l, lam):
        """
        Part of Optimization
        """
        temp = f**2 + l**2
        if isinstance(lam, float):
            return lam*np.dot(temp[0:self.length], self.b_cross_integral_list)
        if isinstance(lam, np.ndarray):
            return sum(lam[0:self.length] * temp[0:self.length] * self.b_cross_integral_list)

    def integral_list(self, S, T):
        """
        Gamma!
        """
        try:
            return self.Integral_List[(S,T)]
        except KeyError:
            result = np.zeros(self.length)
            for k in range(0, self.length):
                lower = max(S, self.T[k])
                upper = min(T, self.T[k + self.d + 1])
                gamma = self.B_Spline.b_integral(k, self.d, upper) - self.B_Spline.b_integral(k, self.d, lower)
                result[k] = gamma
            self.Integral_List[(S,T)] = result
        return result

    def b_cross_integral(self, S, T):
        return np.array([self.B_Spline.b_cross_integral(k, k, S, T)**2 for k in range(0, self.length)])

    def bf_list(self, T):
        return np.array([self.B_Spline.b_function(k, self.d, T) for k in range(0, self.length)])

    def fwd_rate(self, S, T, l):
        return self.libor_fwd_rate(S, T, l)