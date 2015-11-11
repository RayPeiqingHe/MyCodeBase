__author__ = 'Ray'

import Quandl

import pandas as pd

from datetime import datetime

# Handle exception
import sys

class QuandlUtils(object):
    """
    Helper class for accessing Quandl data
    """

    def __init__(self, api_key = None):
        """
        The constructor of the class
        :param api_key: the API key for querying data from Quandl. You can still acess data from Quandl
                        without the API key. But you can only call the Quandl function 50 times per day.

                        To get the API key, you can simply sign up an account on Quandl
        :return:
        """
        self._api_key = api_key

    def get_data(self, quandl_code, start_dt = None, end_dt = None):
        """

        :param quandl_code: To download a dataset, you will need to know its “Quandl code”
                            For example, to get Facebook stock price, use "WIKI/FB"
        :param start_dt: The start date of the data
        :param end_dt: The end date of the data
        :return:
        """

        # First check if start date is a valid date
        if start_dt is not None and type(start_dt) is not datetime.date:
            raise TypeError('start_dt must be a datetime.date, not a %s' % type(start_dt))

        # Then check if end date is a valid date
        if end_dt is not None and type(end_dt) is not datetime.date:
            raise TypeError('end_dt must be a datetime.date, not a %s' % type(end_dt))

        try:
            my_data = Quandl.get(quandl_code, authtoken=self._api_key,trim_start=start_dt, trim_end=end_dt)
        except:
            # catch all exception
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % str(e) )

