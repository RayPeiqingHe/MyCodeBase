__author__ = 'Ray'

from __future__ import division #for 0/0=0 purpose
import numpy as np


class B_Spline(object):
    def __init__(self, time_vectortor):
        """
        B_Spline:  class for B-Spline interpolation with function to calculate Basis Functions and its derivative and integral
        """
        self.T = np.asarray(time_vectortor)
        self.b_function_list = {}

    def __str__(self):
        return "B_Spline"

    def b_function(self, k, d, t):
        if t < self.T[k] or t >= self.T[k+d+1]:
            return 0
        if d == 0:
            return 1
        try:
            return self.b_function_list[(k,d,t)]
        except KeyError:
            part1 = (t - self.T[k]) / (self.T[k+d] - self.T[k])
            part2 = (self.T[k+d+1] - t) / (self.T[k+d+1] - self.T[k+1])
            self.b_function_list[(k,d,t)] = part1 * self.b_function(k, d - 1, t) + part2 * self.b_function(k + 1, d - 1, t)
            return self.b_function_list[(k,d,t)]

    def b_derivative(self, k, d, t):
        if d < 1:
            return 0
        else:
            return self.b_function(k, d - 1, t) * d / (self.T[k + d] - self.T[k]) - self.b_function(k + 1, d - 1, t)* d / (self.T[k + d + 1] - self.T[k + 1])

    def b_integral(self, k, d, t):
        if t < self.T[k]:
            return 0.0
        coef = (self.T[k + d + 1] - self.T[k]) / (d + 1)
        if t >= self.T[k + d + 1]:
            return coef
        else:
            result = 0
            i = k
            while self.T[i] < t:
                result += coef * self.b_function(i, d + 1, t)
                i += 1
            return result
    def b_second_derivative(self, k, d, t, order=2):
        """
        calculate higher order integral, not only second order
        """
        if order <= 0:
            return self.b_function(k, d, t)
        if order == 1:
            return self.b_derivative(k, d, t)
        else:
            part1 = d / (self.T[k + d] - self.T[k])
            part2 = d / (self.T[k + d + 1] - self.T[k + 1])
            return part1 * self.b_second_derivative(k, d - 1, t, order - 1) + part2 * self.b_second_derivative(k + 1, d - 1, t, order - 1)

    def b_cross_integral(self, k, l, a, b):
        """
        cross integral show in lec1 fomula 33 and 34
        """
        part1 = self.b_second_derivative(k, 3, b, 1) * self.b_second_derivative(l, 3, b, 2)
        part2 = self.b_second_derivative(k, 3, a, 1) * self.b_second_derivative(l, 3, a, 2)
        temp = [t for t in self.T if a < t < b]
        length = len(temp)
        temp = [a] + temp + [b]
        part3 = sum(self.b_second_derivative(l, 3, temp[j-1], 3) *(self.b_function(k, 3, temp[j])- self.b_function(k, 3, temp[j-1]))  for j in range(1, length+2))
        return part1 - part2 - part3
