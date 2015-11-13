__author__ = 'Ray'

"""Main file that runs the data input and optimization"""


import sys
import numpy as np
from RateFunctions import Rate_Functions
import MarketRate as mr
import ExcelDataReader as Excel
import MarketRateCalibrator as opimizer

import matplotlib.pyplot as plt


if __name__ == '__main__':

    # ------------------ read data from spreadsheet ----------------
    print "Start Reading market rate from Excel..."
    reader = Excel.ExcelDataReader(r"DataSheetCurve.xls")

    reader.read_data_into_dictionary()

    # --------------------------------------------------------------
    print "Initializing market rate object and calculator..."

    #The years in our knot points
    tvec = range(-3,0) + [0, 1, 2, 3, 5, 7, 10, 15, 20, 25, 31] + range(32, 36)

    #Convert into numpy array
    tvec = np.array(tvec)

    rc = Rate_Functions(tvec)

    #Start generating Market rate object using the input market rate
    swapRateObj = mr.SwapRate(rc, **reader.swap_rate)
    bSwapRateObj = mr.BasisSwapRate(rc, **reader.basis_swap_rate)
    edObj = mr.EuroDollar(rc, **reader.ed_future)
    liborObj = mr.LiborFixing(rc, **reader.libor)
    ffrObj = mr.FedFundRate(rc, **reader.fed_fund)

    # --------------Set up optimization parameters ------------------
    print "Setting up optimization parameters..."

    fitobjs = [swapRateObj, bSwapRateObj, edObj, liborObj]

    # Might need to re-visit the lambda
    #lambdas = np.array([0, 0, 0, 1e-5, 1e-5, 1e-3, 1e-3, 1e-2, 1e-1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    lambdas = 0.0005;

    n = len(tvec)
    x0 = np.repeat(0.01, 2 * n)

    # create optimizer object
    op = opimizer.MarketRateCalibrator(lambdas, tvec, rc, x0, *fitobjs)

    print "Performing optimization..."

    #Invoke the optimizar to find optimal f_k and l_k
    xopt = op.optimize(*fitobjs)

    n = op._n

    fopt, lopt = xopt[:n], xopt[n:]

    #-------------------------------------------------------------
    # ---------- Plot the fitted rates vs. actual rates ----------
    fig = plt.figure()
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    ax1.plot(swapRateObj._tenor_, 100*swapRateObj._rvec_, 'ro')
    ax1.plot(swapRateObj._tenor_, 100*swapRateObj.calibrate(fopt, lopt), 'y-')
    ax1.set_title("Par Swap Rate")
    ax1.legend(("actual", "fitted"))


    ax2.plot(bSwapRateObj._tenor_, 100*bSwapRateObj._rvec_, 'ro')
    ax2.plot(bSwapRateObj._tenor_, 100*bSwapRateObj.calibrate(fopt, lopt), 'y-')
    ax2.set_title("Basis Swap Rate")
    ax2.legend(("actual", "fitted"))


    ax3.plot(edObj._tvec_, 100*edObj._rvec_, 'ro')
    ax3.plot(edObj._tvec_, 100*edObj.calibrate(fopt, lopt), 'y-')

    #ax3.plot(liborObj._tvec_, 100*liborObj._rvec_, 'ro')
    #ax3.plot(liborObj._tvec_, 100*liborObj.calibrate(fopt, lopt), 'y-')
    ax3.set_title("3M LIBOR fwd")
    ax3.legend(("actual", "fitted"))

    xdat = np.linspace(0, 30, 100)
    y_lib = map(lambda t: rc.inst_libor_fwd_rate(t, lopt), xdat)
    ax4.plot(xdat, 100*np.asarray(y_lib))

    #y_bsr = map(lambda t: rc.libor_ois_spread(0, t, fopt, lopt), xdat)
    y_bsr = map(lambda t: rc.inst_ois_fwd_rate(t, fopt), xdat)

    ax4.plot(xdat, 100*np.asarray(y_bsr))
    #ax4.set_title("Inst. 3M LIBOR and LIBOR/OIS Spread")
    #ax4.legend(("inst LIBOR", "LIBOR/OIS spread"))
    ax4.set_title("Inst. 3M LIBOR and Inst. 3M OIS")
    ax4.legend(("inst LIBOR", "inst OIS"))

    plt.show()
