__author__ = 'Ray'

from QuandlUtils import *

import matplotlib.pyplot as plt


class FutureCaseStudy(object):
    """
    class for the case study project.
    """

    # The column position of last price in the future price table
    LAST_POS = 4

    # The column position of the Total Reportable Longs column in the CTR table
    TOT_LONG = 13

    # The column position of the Total Reportable Shorts column in the CTR table
    TOT_SHORT = 14

    def __init__(self, api_key = None):

        """The constructor of the class

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

    def get_future_price(self, start_dt = None, end_dt = None,):
        """This function pulls future data from Quandl

        :param start_dt: The start date of the data
        :param end_dt: The end date of the data
        :return: The data frame of the future pricing and return data
        """

        # the name of the column from the future table we are interested in
        cols = [self._soy_price + '.' +  str(FutureCaseStudy.LAST_POS),
                self._soy_oil_price + '.' +  str(FutureCaseStudy.LAST_POS)]

        # Call the Quandl utility class to pull data from Quandl
        prices = self._quandl.get_data(cols, start_dt, end_dt)

        cols = ['Soybean', 'Soybean_oil']

        for i in range(0, 2):
            # Compute the daily return
            prices[cols[i] + '_daily_ret'] = prices.iloc[:,i] / \
                                    prices.shift(1).iloc[:,i] - 1

            # Compute the historical cumulative return
            prices[cols[i] + '_cumu_ret'] = prices.iloc[:,i] / \
                                    prices.iloc[0,i]

        return prices

    def get_ctr(self, start_dt = None, end_dt = None):
        """This function pulls Commitment of Traders Report  from Quandl

        :param start_dt: The start date of the data
        :param end_dt: The end date of the data
        :return: The data frame of the Commitment of Traders Report
        """

        # the list of the columns we are interested from the Commitment of Traders Report
        cols = [self._soy_CTR + '.' +  str(FutureCaseStudy.TOT_LONG),
                self._soy_CTR + '.' +  str(FutureCaseStudy.TOT_SHORT),
                self._soy_oil_CTR + '.' +  str(FutureCaseStudy.TOT_LONG),
                self._soy_oil_CTR + '.' +  str(FutureCaseStudy.TOT_SHORT)]

        # Call the Quandl utility class to pull data from Quandl
        CTR_report = self._quandl.get_data(cols, start_dt, end_dt)

        cols = ['Soybean', 'Soybean_oil']

        for i in range(0, 2):
            # Compute the long short ratio
            CTR_report[cols[i] + '_LS_RATIO'] = CTR_report.iloc[:,2 * i] / \
                                CTR_report.iloc[:,2 * i + 1]

        return CTR_report

    @staticmethod
    def plot_dataframe(df, col, axis_label, save_file = None, display_plot = True):
        """This function plot the specific column of the input data frame.
            If a file name is given, this function will save the plot into the file.

        :param df: The data frame containing the historical prices
        :param col: The specific column in the data frame to be plotted
        :param axis_label: the custom label of the axises. The first one is the label of the x axis
                        The second is the label of the y axis
        :param save_file: the name of the file where we want to save the plot
        :param display_plot: a boolean to indicate if we want to display the plot
        """

        ax = df[col].plot(figsize=(14, 10),grid=True)

        ax.set_xlabel(axis_label[0])

        ax.set_ylabel(axis_label[1])

        if save_file is not None:
            fig = ax.get_figure()
            fig.savefig(save_file)

        if display_plot:
            plt.show()

    def compute_corr(self, hist_daily_return, cols):
        """This function compute the return correlation between between soybean and soybean oil

        :param hist_daily_return: The data frame containing the return data of the future data of interest
        :param cols: The list of the column names for the correlation computation
        :return: a numpy matrix containing the correlation matrix
        """

        # Create a data frame that just contains the two columns in which
        # We are interested in their coorelation
        data = hist_daily_return[cols]

        # Compute the correlation
        corr = data.corr()

        try:
            corr = data.corr()
        except:
            # catch all exception
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % str(e) )

        return corr



