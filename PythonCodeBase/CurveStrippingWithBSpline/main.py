from __future__ import division, print_function, absolute_import
import scipy.optimize as sco
import xlrd
import numpy as np
from BsplineBasis import BsplineBasis
from MarketObject import IrSwap, BasisSwap, BaseCurve
from Bspline import Bspline


# Libor rate
libor_fwd_rates = []
# fed fund rate
ois_rates = []
# Swap Rate
swap_rates = []

basis_swap_rates = []


def get_data():
    # ------------------ read data from spreadsheet ----------------
    data_file = '/home/darthray/Documents/dev/MySearch/Assignment1/' + \
                'Programming_Assignment_1/DataSheetCurve.xls'

    print("Reading data from spreadsheet...")

    wb = xlrd.open_workbook(data_file)

    sh2 = wb.sheet_by_index(1)

    fields1 = ['rate', 'Spot Date', 'tenor']

    # We use *args since we don't know number of data points in advance
    def make_dict(fields, from_row, to_row, *col):
        values = [sh2.col_values(x, from_row, to_row) for x in col]
        return dict(zip(fields, values))

    libor = make_dict(fields1, 2, 4, 4, 5, 6)
    ed_future = make_dict(fields1, 6, 14, 5, 6, 7)
    swap_rate = make_dict(fields1, 16, 27, 4, 5, 6)
    fed_fund = make_dict(fields1, 29, 30, 4, 5, 6)
    basis_swap_rate = make_dict(fields1, 33, 49, 4, 5, 6)

    # Libor Rate
    populate_market_data(libor_fwd_rates, libor)

    populate_market_data(libor_fwd_rates, ed_future)

    # ois rate
    populate_market_data(ois_rates, fed_fund)

    # Swap Rate
    populate_market_data(swap_rates, swap_rate)

    # basis swap spread
    basis_swap_rate['rate'] = [rate / 1e4 for rate in basis_swap_rate['rate']]

    populate_market_data(basis_swap_rates, basis_swap_rate)


def populate_market_data(rates_list, raw_data):
    for i in range(len(raw_data['Spot Date'])):
        rate = MarketData(raw_data['Spot Date'][i], raw_data['tenor'][i], raw_data['rate'][i])

        rates_list.append(rate)


class MarketData(object):
    def __init__(self, spot_date, tenor, rate):
        self.spot_date = spot_date

        self.tenor = tenor

        self.rate = rate

    def __str__(self):
        return 'spot date : {0} tenor : {1} rate : {2}'.\
            format(self.spot_date, self.tenor, self.rate)


def objective_function(ctl_pts):
    libor_ctl_pts = ctl_pts[:int(len(ctl_pts) / 2)]

    ois_ctl_pts = ctl_pts[int(len(ctl_pts) / 2):]

    libor_b_spline = Bspline(basis_funcs, libor_ctl_pts)

    ois_b_spline = Bspline(basis_funcs, ois_ctl_pts)

    libor_curve = BaseCurve(libor_b_spline)

    ois_curve = BaseCurve(ois_b_spline)

    obj_func = 0

    for rate in libor_fwd_rates:
        obj_func += (rate.rate - libor_curve.forward_rate(rate.spot_date, rate.spot_date + rate.tenor)) ** 2

    for rate in ois_rates:
        obj_func += (rate.rate - ois_curve.forward_rate(rate.spot_date, rate.spot_date + rate.tenor)) ** 2

    for rate in swap_rates:
        swap = IrSwap(rate.spot_date, rate.tenor, ois_curve, libor_curve)
        obj_func += (rate.rate - swap.get_swap_rate()) ** 2

    for rate in basis_swap_rates:
        swap = BasisSwap(rate.spot_date, rate.tenor, ois_curve, libor_curve)

        obj_func += (rate.rate - swap.get_basis_spread()) ** 2

    obj_func += lambdas * (libor_b_spline.cross_integral(T0, T_max) + ois_b_spline.cross_integral(T0, T_max))

    return obj_func


if __name__ == '__main__':
    # The years in our knot points
    tvec = range(-3, 0) + [0, 1, 2, 3, 5, 7, 10, 15, 20, 25, 31] + range(32, 36)

    tvec = range(-3, 0) + [0, 1, 2, 3, 5, 7, 10, 15, 20, 25, 35] + range(36, 40)

    order = 3

    basis_funcs = BsplineBasis(tvec, order)

    lambdas = 0.0005

    T0 = 0

    T_max = 30

    ctl_pts0 = np.repeat(0.01, 2 * len(tvec))

    res = sco.minimize(objective_function, ctl_pts0, method='BFGS', tol=1e-8, options={'disp': True})

    libor_ctl_pts = res['x'][:int(len(res['x']) / 2)]

    ois_ctl_pts = res['x'][int(len(res['x']) / 2):]

    libor_b_spline = Bspline(basis_funcs, libor_ctl_pts)

    ois_b_spline = Bspline(basis_funcs, ois_ctl_pts)

    libor_curve = BaseCurve(libor_b_spline)

    ois_curve = BaseCurve(ois_b_spline)

    libor_curve.plot()

    ois_curve.plot()
