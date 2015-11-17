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
        if S == T:
            return self.inst_libor_fwd_rate(S, l)
        else:
            return  (exp(np.dot(l[0:self.length], self.integral_list(S,T))) - 1) / (T - S)

    def PV_Swap(self,tenor,fixed_rate,fopt,lopt,N=100,T_0=0):
        day_count_fix = 2
        day_count_float = 4
        annuity = 0.0
        for t in range(1, int(round(day_count_fix * tenor)) + 1):
            annuity += self.disc_factor(0, t, fopt)/day_count_fix
        p_float = 0.0
        for t in range(1, int(round(day_count_float * tenor)) + 1):
                p_float += self.libor_fwd_rate( (t - 1) / day_count_float, t / day_count_float, lopt) *  self.disc_factor(0, t / day_count_float, fopt)/day_count_float
        return N*(fixed_rate*annuity-p_float)

    def swap_rate(self, T_0, tenor, ffr, lbr, f_0 = 0):
        fix_freq, float_freq = 2, 4
        annuity = 0 #annuity function
        for t in xrange(1, int(round(fix_freq * tenor)) + 1):
            #annuity += self.disc_factor(0, T_0 + t / fix_freq, ffr)
            annuity += self.disc_factor(0, T_0 + t / fix_freq, ffr) / fix_freq

        p_float = 0
        for t in xrange(1, int(round(float_freq * tenor)) + 1):
            lr = self.libor_fwd_rate( (t - 1) / float_freq, t / float_freq, lbr)

            if t == 1 and f_0 != 0:
                lr = f_0

            p_float += lr * self.disc_factor(0, T_0 + t / float_freq, ffr) / float_freq

        ret = p_float / annuity
        return ret

    def ois_fwd_rate(self, S, T, f):
        if S == T:
            return self.inst_ois_fwd_rate(S, f)
        else:
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

    def Tikhonov_regularizer(self, ffr, lbr, lam, T_0, T_max):
        """
        Compute the Tikhonov regularizer in the objective function
        :param ffr: from index -3 to N
        :param lbr: from index -3 to N
        :param lam: lambda in the Tikhonov regularizer
        :param T_0: The beginning time
        :param T_max: The ending time
        :return:
        """
        f_square = self.B_Spline.sec_deriv_integral_square(ffr[0:self.length], T_0, T_max)

        l_square = self.B_Spline.sec_deriv_integral_square(lbr[0:self.length], T_0, T_max)

        return lam * (f_square + l_square)
        """
        temp = f**2 + l**2
        if isinstance(lam, float):
            return lam*np.dot(temp[0:self.length], self.b_cross_integral_list)
        if isinstance(lam, np.ndarray):
            return sum(lam[0:self.length] * temp[0:self.length] * self.b_cross_integral_list)
        """
    def integral_list(self, S, T):
        """
        Gamma!
        """
        try:
            return self.Integral_List[(S,T)]
        except KeyError:
            result = np.zeros(self.length)
            for k in range(0, self.length):
                #Bug fix: if T < self.T[k], make it 0
                if T <= self.T[k]:
                    result[k] = 0
                    continue
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
    def bf(self, T):
        return self.bf_list(self, T)