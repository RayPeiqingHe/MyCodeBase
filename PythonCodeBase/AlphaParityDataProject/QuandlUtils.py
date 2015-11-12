__author__ = 'Ray'

import Quandl

from datetime import datetime


class QuandlCodeHelper(object):

    """
    This class contains helper class to construct the list of columns to query.
    For multiple datatable that has a similar structure, we can typically query
    all of the data at once. This helper class provide function to construct the query.
    """

    def __init__(self, quandl_codes, columns_pos = None):
        """The constructor of the class

        :param quandl_codes: It is equivalent to the name of the source table. It value can be
            either a string ot a llst of string
            To find the quandl_code for a particular data, you can always run the
            search method from Quandl.

            For exmaple: Quandl.search('OIL'). The output will be

            {u'code': u'NSE/OIL',
             u'colname': [u'Date',
             u'Open',
             u'High',
            u'Low',
            u'Last',
            u'Close',
            u'Total Trade Quantity',
            u'Turnover (Lacs)'],
            u'desc': u'Historical prices for Oil India Limited (OIL), (ISIN: INE274J01014),
            National Stock Exchange of India.',
            u'freq': u'daily',
            u'name': u'Oil India Limited'}
        :param  columns_pos: The column position in the Quandl table. You can also find it from
            the search function
        """

        self._quandl_codes = quandl_codes

        self._columns_pos = columns_pos

    def get_query_cols(self):
        """This method dynamicly construct the list of columns to query from Quandl"""

        if self._columns_pos is None or len(self._columns_pos) == 0:
            # If no column position is specified, just return the Quandl code
            return self._quandl_codes
        else:
            # Otherwise dynamicly construct the list of columns to query
            cols = [t + '.' + str(s) for t in self._quandl_codes for s in self._columns_pos]

            return cols


class QuandlUtils(object):

    """
    Wrapper class for accessing Quandl data. This class is mainly for providing
    more detailed info for handling input arugument error, such as invalid dates
    and invalid Quandl code.
    """

    def __init__(self, api_key = None):

        """The constructor of the class

        :param api_key: the API key for querying data from Quandl. You can still acess data from Quandl
                        without the API key. But you can only call the Quandl function 50 times per day.

                        To get the API key, you can simply sign up an account on Quandl
        """

        # Store the API key
        self._api_key = api_key

    def get_data(self, quandl_code, start_dt = None, end_dt = None):

        """This function pulls data from Quandl

        :param quandl_code: To download a dataset, you will need to know its Quandl code
                            For example, to get Facebook stock price, use "WIKI/FB"
        :param start_dt: The start date of the data
        :param end_dt: The end date of the data
        :return: The resulted data frame containing the Quandl data
        """

        # First check if start date is a valid date
        if start_dt is not None and type(start_dt) is not datetime:
            # Raise error if start_dt is a invalid date time
            raise TypeError('start_dt must be a datetime.date, not a %s' % type(start_dt))

        # Then check if end date is a valid date
        if end_dt is not None and type(end_dt) is not datetime:
            # Raise error if end_dt is a invalid date time
            raise TypeError('end_dt must be a datetime.date, not a %s' % type(end_dt))

        # Call the Quandl DLL to pull down quandl data
        quandl_data = Quandl.get(quandl_code, authtoken=self._api_key,trim_start=start_dt, trim_end=end_dt)

        # Check if the data frame is empty
        if quandl_data.empty:
            # If so, it is likely that the quandl_code is invalid
            raise ValueError('Make sure {0} are valid Quandl codes'.format(quandl_code))

        return quandl_data






