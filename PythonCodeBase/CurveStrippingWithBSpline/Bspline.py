import numpy as np


class Bspline(object):

    def __init__(self, basis_funcs, clt_pts):
        self.basis_fns = basis_funcs

        self.clt_pts = clt_pts

    def __call__(self, xi):
        tmp = self.basis_fns(xi)

        return np.sum(tmp * self.clt_pts[:len(tmp)])

    def integrate(self, S, T):
        tmp = self.basis_fns.integrate(S, T)

        return np.sum(tmp * self.clt_pts[:len(tmp)])

    def d(self, xi, deriv_order):
        tmp = self.basis_fns.d(xi, deriv_order=deriv_order) \
            if deriv_order > 0 else self.basis_fns(xi)

        return np.sum(tmp * self.clt_pts[:len(tmp)])

    def cross_integral(self, a, b):
        tmp = self.basis_fns.cross_product_integral(a, b)

        tmp2 = np.outer(self.clt_pts, self.clt_pts)[:tmp.shape[0], :tmp.shape[1]]

        return np.sum(tmp * tmp2)
