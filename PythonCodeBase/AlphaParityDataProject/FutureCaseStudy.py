__author__ = 'Ray'

from QuandlUtils import *

import matplotlib.pyplot as plt


class FutureCaseStudy(object):
    """
    class for the case study project.
    """

    def __init__(self, api_key = None):

        """The constructor of the class

        :param api_key: the API key for querying data from Quandl. You can still acess data from Quandl
                        without the API key. But you can only call the Quandl function 50 times per day.

                        To get the API key, you can simply sign up an account on Quandl
        """

        # Initialize the Quandl data utility function
        self._quandl = QuandlUtils(api_key)

    def get_future_price(self, quandl_codes, cols, start_dt = None, end_dt = None):
        """This function pulls future data from Quandl

        :param start_dt: The start date of the data
        :param end_dt: The end date of the data
        :return: The data frame of the future pricing and return data
        """

        # Call the Quandl utility class to pull data from Quandl
        prices = self._quandl.get_data(quandl_codes, start_dt, end_dt)

        for i in range(0, len(cols)):
            # Compute the daily return
            prices[cols[i] + '_daily_ret'] = prices.iloc[:,i] / \
                                    prices.shift(1).iloc[:,i] - 1

            # Compute the historical cumulative return
            prices[cols[i] + '_cumu_ret'] = prices.iloc[:,i] / \
                                    prices.iloc[0,i]

        return prices

    def get_ctr(self, quandl_codes, cols, start_dt = None, end_dt = None):
        """This function pulls Commitment of Traders Report  from Quandl

        :param start_dt: The start date of the data
        :param end_dt: The end date of the data
        :return: The data frame of the Commitment of Traders Report
        """

        # Call the Quandl utility class to pull data from Quandl
        CTR_report = self._quandl.get_data(quandl_codes, start_dt, end_dt)

        for i in range(0, len(cols)):
            # Compute the long short ratio
            CTR_report[cols[i] + '_LS_RATIO'] = CTR_report.iloc[:,2 * i] / \
                                CTR_report.iloc[:,2 * i + 1]

        return CTR_report

    def visualize_data(self, df_prices, df_soybean_ctr, cols):
        """This function generate chart of cumulative return and long short ratio

        :param df_prices: Data frame containing the pricing data
        :param df_soybean_ctr: Data frame containing the CFTC Commitment of Traders Report
        :param cols: The list of the asset names used as the output file
        """

        axis_label = ['Date', 'cumulative return']

        # Plot the cumulative return for soybean future
        FutureCaseStudy.plot_dataframe(df_prices, cols[0] + '_cumu_ret', axis_label,
                                       'Soy bean cumulative return', cols[0] + '_return.pdf')

        # Plot the cumulative return for soybean oil future
        FutureCaseStudy.plot_dataframe(df_prices, cols[1] + '_cumu_ret', axis_label,
                                       'Soy bean oil cumulative return', cols[1] + '_return.pdf')

        axis_label = ['Date', 'long short ratio']

        # Plot the logn short ratio for soybean future
        FutureCaseStudy.plot_dataframe(df_soybean_ctr, cols[0] + '_LS_RATIO', axis_label,
                                       'Soy bean Total Long Short ratio', cols[0] + '_LS_ratio.pdf')

        # Plot the logn short ratio for soybean oil future
        FutureCaseStudy.plot_dataframe(df_soybean_ctr, cols[1] + '_LS_RATIO', axis_label,
                                       'Soy bean oil Total Long Short ratio', cols[1] + '_LS_ratio.pdf')

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

        return corr

    @staticmethod
    def plot_dataframe(df, col, axis_label, title, save_file = None, display_plot = True):
        """This function plot the specific column of the input data frame.
            If a file name is given, this function will save the plot into the file.

        :param df: The data frame containing the historical prices
        :param col: The specific column in the data frame to be plotted
        :param axis_label: the custom label of the axises. The first one is the label of the x axis
                        The second is the label of the y axis
        :param title: The title of the chart
        :param save_file: the name of the file where we want to save the plot
        :param display_plot: a boolean to indicate if we want to display the plot
        """

        ax = df[col].plot(figsize=(14, 10),grid=True,title=title)

        ax.set_xlabel(axis_label[0])

        ax.set_ylabel(axis_label[1])

        if save_file is not None:
            fig = ax.get_figure()
            fig.savefig(save_file)

        if display_plot:
            plt.show()














