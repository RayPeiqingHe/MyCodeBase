__author__ = 'Ray'

from QuandlUtils import *

#Using the argparse library
import argparse

class FutureCaseStudy(object):
    """

    """

    def __init__(self, api_key = None):
        """

        :return:
        """

        # I am using the following data
        # Soybean future contract Quandl code: CHRIS/CME_S1
        # Soybean Oil Futures Quandl code: CHRIS/CME_BO1
        # Soybeans CTR Quandl code: CFTC/S_F_ALL
        # Soybeans oil CTR Quandl code: CFTC/BO_F_ALL

        self.quandl_codes = ['CHRIS/CME_S1', 'CHRIS/CME_BO1', 'CFTC/S_F_ALL', 'CFTC/BO_F_ALL']

        # Initialize the Quandl data utility function
        self.quandl = QuandlUtils(api_key)

        self.future_data = None

    def get_future_data(self, start_dt = None, end_dt = None):
        """

        :return:
        """

        self.quandl.get_data('CHRIS/CME_S1', start_dt, end_dt)

        self.future_data = self.quandl.quandl_data

