from __future__ import division, print_function, absolute_import
from Memoize import Memoize
import numpy as np


class BsplineBasis(object):
    """Numpy implementation of Cox - de Boor algorithm in 1D."""

    def __init__(self, knot_vector, order):
        """Create a Bspline object.

        Parameters:
            knot_vector: Python list or rank-1 Numpy array containing knot vector
                         entries. Notice that it should include the extra order number of
                         poins at the front and rear
            order: Order of interpolation, e.g. 0 -> piecewise constant between
                   knots, 1 -> piecewise linear between knots, etc.

        Returns:
            Bspline object, callable to evaluate basis functions at given
            values of `x` inside the knot span.
        """
        kv = np.atleast_1d(knot_vector)
        if kv.ndim > 1:
            raise ValueError("knot_vector must be Python list or rank-1 array, but got rank = %d" % kv.ndim)
        self.knot_vector = kv

        order = int(order)
        if order < 0:
            raise ValueError("order must be integer >= 0, but got %d" % order)

        self.p = order

        # Dummy calls to the functions for memory storage
        self.__call__(0.0)
        self.d(0.0)

    def __basis0(self, xi):
        """Order zero basis (for internal use)."""
        return np.where(np.all([self.knot_vector[:-1] <= xi,
                                xi < self.knot_vector[1:]], axis=0), 1.0, 0.0)

    def __basis(self, xi, p, deriv_order=0):
        """Recursive Cox - de Boor function (for internal use).

        Compute basis functions and optionally their first derivatives.
        """

        if p == 0:
            return self.__basis0(xi)
        else:
            # basis_p_minus_1 = self.__basis(xi, p - 1)
            deriv_order_minus_1 = max(deriv_order - 1, 0)

            if p > self.p:  # Assume one order higher
                basis_p_minus_1 = self.__call__(xi)
            elif deriv_order_minus_1 == 0:
                basis_p_minus_1 = self.__basis(xi, p - 1)
            else:
                basis_p_minus_1 = self.d(xi, p - 1, deriv_order_minus_1)

        first_term_numerator = xi - self.knot_vector[:-p]
        first_term_denominator = self.knot_vector[p:] - self.knot_vector[:-p]

        second_term_numerator = self.knot_vector[(p + 1):] - xi
        second_term_denominator = (self.knot_vector[(p + 1):] -
                                   self.knot_vector[1:-p])

        # Change numerator in last recursion if derivatives are desired
        # if deriv_order > 0 and p == self.p:
        if deriv_order > 0:
            first_term_numerator = p
            second_term_numerator = -p

        # Disable divide by zero error because we check for it
        with np.errstate(divide='ignore', invalid='ignore'):
            first_term = np.where(first_term_denominator != 0.0,
                                  (first_term_numerator /
                                   first_term_denominator), 0.0)
            second_term = np.where(second_term_denominator != 0.0,
                                   (second_term_numerator /
                                    second_term_denominator), 0.0)

        # Each return trim off the last basis function value
        # that is why the number the element decrease as order increases
        tmp = (first_term[:-1] * basis_p_minus_1[:-1] +
               second_term * basis_p_minus_1[1:])

        return tmp

    @Memoize
    def __call__(self, xi, p=None):
        """Convenience function to make the object callable.  Also 'memoized' for speed.

        Returns:
            the array of basis functions computed at xi of each knot points
        """

        # print('basis function is called {0}, {1}'.format(xi, p))

        return self.__basis(xi, self.p if p is None else p)

    @Memoize
    def d(self, xi, p=None, deriv_order=1):
        """Convenience function to compute first derivative of basis functions. 'Memoized' for speed.


        Returns:
            the array of first derivative of basis functions omputed at xi of each knot points
        """

        power = self.p if p is None else p

        assert power >= deriv_order, "derivative order {0} must be greater than basis order {1}". \
            format(deriv_order, power)

        return self.__basis(xi, power, deriv_order)

    @Memoize
    def integrate_base(self, t):
        """Convenience function to compute the integral of spline function. 'Memoized' for speed.

        Returns:
            the array of integral from minus infinity to xi of each knot points
        """

        return self.__integrate_base(t)

    def integrate(self, s, t):
        return self.integrate_base(t) - self.integrate_base(s)

    def __integrate_base(self, t):
        # Remember that self.spline_order_plus_1 is of order of p + 1
        p = self.p + 1

        basis_functions = self.__call__(t, p)

        coeffs = (self.knot_vector[p:] - self.knot_vector[:-p]) / p

        # an array containing the reverse running sum
        basis_sums = np.cumsum(basis_functions[::-1])[::-1]

        size = min(len(basis_sums), len(coeffs))

        return basis_sums[:size] * coeffs[:size]

    @Memoize
    def cross_product_integral(self, a, b):
        """Convenience function to compute the integral of spline function. 'Memoized' for speed.

        Returns:
            The cross product used in the optimizer
        """

        return self._cross_product_integral(a, b)

    def _cross_product_integral(self, a, b):
        d_2_b = self.d(b, deriv_order=2)

        d_1_b = self.d(b, deriv_order=1)

        d_2_a = self.d(a, deriv_order=2)

        d_1_a = self.d(a, deriv_order=1)

        outer_b = np.outer(d_2_b, d_1_b)

        outer_a = np.outer(d_2_a, d_1_a)

        knot_pts = self.knot_vector[(self.knot_vector > a) & (self.knot_vector < b)]

        knot_pts = [a] + list(knot_pts) + [b]

        sum_of_pts = np.zeros(outer_b.shape)
        for i in xrange(len(knot_pts) - 1):
            d_3_l = self.d(knot_pts[i], deriv_order=3)

            d_0_k_j = self.__call__(knot_pts[i + 1])

            d_0_k_j_1 = self.__call__(knot_pts[i])

            tmp = np.outer(d_3_l, d_0_k_j - d_0_k_j_1)

            sum_of_pts += tmp

        return outer_b - outer_a - sum_of_pts

    def plot(self):
        """Plot basis functions over full range of knots.

        Convenience function. Requires matplotlib.
        """

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            from sys import stderr
            print("ERROR: matplotlib.pyplot not found, matplotlib must be installed to use this function", file=stderr)
            raise

        x_min = np.min(self.knot_vector)
        x_max = np.max(self.knot_vector)

        x = np.linspace(x_min, x_max, num=1000)

        ns = np.array([self(i) for i in x]).T

        for n in ns:
            plt.plot(x, n)

        return plt.show()

    def dplot(self):
        """Plot first derivatives of basis functions over full range of knots.

        Convenience function. Requires matplotlib.
        """

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            from sys import stderr
            print("ERROR: matplotlib.pyplot not found, matplotlib must be installed to use this function", file=stderr)
            raise

        x_min = np.min(self.knot_vector)
        x_max = np.max(self.knot_vector)

        x = np.linspace(x_min, x_max, num=1000)

        ns = np.array([self.d(i) for i in x]).T

        for n in ns:
            plt.plot(x, n)

        return plt.show()

    def __diff_internal(self):
        """Differentiate a B-spline once, and return the resulting coefficients and Bspline objects.

        This preserves the Bspline object nature of the data, enabling recursive implementation
        of higher-order differentiation (see `diff`).

        The value of the first derivative of `B` at a point `x` can be obtained as::

        def diff1(B, x):
            terms = B.__diff_internal()
            return sum( ci*Bi(x) for ci,Bi in terms )

        Returns:
            tuple of tuples, where each item is (coefficient, Bspline object).

        See:
           `diff`: differentiation of any order >= 0
        """
        assert self.p > 0, "order of Bspline must be > 0"  # we already handle the other case in diff()

        # https://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-derv.html
        #
        t = self.knot_vector
        p = self.p
        bi = BsplineBasis(t[:-1], p - 1)
        bip1 = BsplineBasis(t[1:], p - 1)

        numer1 = +p
        numer2 = -p
        denom1 = t[p:-1] - t[:-(p + 1)]
        denom2 = t[(p + 1):] - t[1:-p]

        with np.errstate(divide='ignore', invalid='ignore'):
            ci = np.where(denom1 != 0., (numer1 / denom1), 0.)
            cip1 = np.where(denom2 != 0., (numer2 / denom2), 0.)

        return (ci, bi), (cip1, bip1)

    def diff(self, order=1):
        """Differentiate a B-spline `order` number of times.

        Parameters:
            order:
                int, >= 0

        Returns:
            **lambda** `x`: ... that evaluates the `order`-th derivative of `B` at the point `x`.
                    The returned function internally uses __call__, which is 'memoized' for speed.
        """
        order = int(order)
        if order < 0:
            raise ValueError("order must be >= 0, got %d" % order)

        if order == 0:
            return self.__call__

        if order > self.p:  # identically zero, but force the same output format as in the general case
            dummy = self.__call__(0.)  # get number of basis functions and output dtype
            nbasis = dummy.shape[0]
            return lambda x: np.zeros((nbasis,), dtype=dummy.dtype)  # accept but ignore input x

        # At each differentiation, each term maps into two new terms.
        # The number of terms in the result will be 2**order.
        #
        # This will cause an exponential explosion in the number of terms for high derivative orders,
        # but for the first few orders (practical usage; >3 is rarely needed) the approach works.
        #
        terms = [(1., self)]
        for k in range(order):
            tmp = []
            for Ci, Bi in terms:
                tmp.extend((Ci * cn, Bn) for cn, Bn in Bi.__diff_internal())  # NOTE: also propagate Ci
            terms = tmp

        # perform final summation at call time
        return lambda x: sum(ci * Bi(x) for ci, bi in terms)

    def collmat(self, tau, deriv_order=0):
        """Compute collocation matrix.

        Parameters:
            tau:
                Python list or rank-1 array, collocation sites
            deriv_order:
                int, >=0, order of derivative for which to compute the collocation matrix.
                The default is 0, which means the function value itself.

        Returns:
            A:
                if len(tau) > 1, rank-2 array such that
                    A[i,j] = D**deriv_order B_j(tau[i])
                where
                    D**k  = kth derivative (0 for function value itself)

                if len(tau) == 1, rank-1 array such that
                    A[j]   = D**deriv_order B_j(tau)

        Example:
            If the coefficients of a spline function are given in the vector c, then::

                np.sum( A*c, axis=-1 )

            will give a rank-1 array of function values at the sites tau[i] that were supplied
            to `collmat`.

            Similarly for derivatives (if the supplied `deriv_order`> 0).

        """
        # get number of basis functions and output dtype
        dummy = self.__call__(0.)
        nbasis = dummy.shape[0]

        tau = np.atleast_1d(tau)
        if tau.ndim > 1:
            raise ValueError("tau must be a list or a rank-1 array")

        a = np.empty((tau.shape[0], nbasis), dtype=dummy.dtype)
        f = self.diff(order=deriv_order)
        for i, taui in enumerate(tau):
            a[i, :] = f(taui)

        return np.squeeze(a)
