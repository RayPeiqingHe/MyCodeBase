__author__ = 'Ray'

from QuandlUtils import *

import matplotlib.pyplot as plt


class FutureCaseStudy(object):
    """
    class for the case study project
    """

    # Output column from quandl for last price
    LAST_PRICE_COL = 'Last'

    # Output column from quandl for Total Reportable Longs
    TOT_LONG_COL = 'Total Reportable Longs'

    # Output column from quandl for Total Reportable Longs
    TOT_SHORT_COL = 'Total Reportable Shorts'

    # The column position of last price in the future price table
    LAST_POS = 4

    # The column position of the Total Reportable Longs column in the CTR table
    TOT_LONG = 13

    # The column position of the Total Reportable Shorts column in the CTR table
    TOT_SHORT = 14

    def __init__(self, api_key = None):

        """
        The constructor of the class

        :param api_key: the API key for querying data from Quandl. You can still acess data from Quandl
                        without the API key. But you can only call the Quandl function 50 times per day.

                        To get the API key, you can simply sign up an account on Quandl
        """

        # I am using the following data
        # Soybean future contract Quandl code: CHRIS/CME_S1
        self._soy_price = 'CHRIS/CME_S1'

        # Soybean Oil Futures Quandl code: CHRIS/CME_BO1
        self._soy_oil_price = 'CHRIS/CME_BO1'

        # Soybeans CTR Quandl code: CFTC/S_F_ALL
        self._soy_CTR = 'CFTC/S_F_ALL'

        # Soybeans oil CTR Quandl code: CFTC/BO_F_ALL
        self._soy_oil_CTR = 'CFTC/BO_F_ALL'

        # Initialize the Quandl data utility function
        self._quandl = QuandlUtils(api_key)

        # Store the historical future prices
        self._prices = None

        # Store the historical Commitment of Traders Report
        self._CTR_report = None

    def get_future_price(self, quandl_code, start_dt = None, end_dt = None):
        """
        This function pulls future data from Quandl

        :param quandl_code: The quandl code of the requested data

        :param start_dt: The start date of the data

        :param end_dt: The end date of the data
        """

        # the name of the column from the future table we are interested in
        cols = quandl_code + '.' +  str(FutureCaseStudy.LAST_POS)

        # Call the Quandl utility class to pull data from Quandl
        self._prices = self._quandl.get_data(cols, start_dt, end_dt)

        # Compute the historical cumulative return
        self._prices['CUM_RET'] = self._prices[FutureCaseStudy.LAST_PRICE_COL] / \
                                self._prices[FutureCaseStudy.LAST_PRICE_COL][0]

    def get_ctr(self, quandl_code, start_dt = None, end_dt = None):
        """
        This function pulls future data from Quandl

        :param quandl_code: The quandl code of the requested data

        :param start_dt: The start date of the data

        :param end_dt: The end date of the data
        """

        # the list of the columns we are interested from the Commitment of Traders Report
        cols = [quandl_code + '.' +  str(FutureCaseStudy.TOT_LONG),
                quandl_code + '.' +  str(FutureCaseStudy.TOT_SHORT)]

        # Call the Quandl utility class to pull data from Quandl
        self._CTR_report = self._quandl.get_data(cols, start_dt, end_dt)

        # Compute the long short ratio
        self._CTR_report['LS_RATIO'] = self._CTR_report[FutureCaseStudy.TOT_LONG_COL] / \
                                self._CTR_report[FutureCaseStudy.TOT_SHORT_COL]

    @staticmethod
    def plot_cum_daily_return(self, df, col, axis_label, save_file = None):
        """
        This function plot the specific column of the input data frame. If a file name is given,
        this function will save the plot into the file.

        :param df: The data frame containing the historical prices

        :param col: The specific column in the data frame to be plotted

        :param axis_label: the custom label of the axises. The first one is the label of the x axis
                        The second is the label of the y axis

        :param save_file: the name of the file where we want to save the plot
        """

        ax = df[col].plot()

        ax.set_xlabel(axis_label[0])

        ax.set_xlabel(axis_label[1])

        if save_file is not None:
            fig = ax.get_figure()
            fig.savefig(save_file)




