__author__ = 'Ray'

import Quandl

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
        """

        # Store the API key
        self._api_key = api_key

        # A dictionary tp store the download data from Quandl
        self.quandl_data = None

    def get_data(self, quandl_code, start_dt = None, end_dt = None):

        """
        This function pulls data from Quandl

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

        try:
            quandl_data = Quandl.get(quandl_code, authtoken=self._api_key,trim_start=start_dt, trim_end=end_dt)

            return quandl_data
        except:
            # catch all exception
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % str(e) )

    def store_data_in_file(self, file_name, file_type = 'csv'):

        """
        This export the quandl data into a file

        :param file_name: The name of the output file

        :param file_type: The type of the output file. Currently it only support csv and Excel format
        """

        if self.quandl_data is None:
            raise ValueError('You need to first query data from Quandl by calling get_data method')

        if file_type == 'csv':
            self.quandl_data.to_csv(file_name)
        elif file_type == 'xlsx':
            self.quandl_data.to_excel(file_name, sheet_name='Sheet1')
        else:
            raise ValueError('Invliad file type!')

    def select_data_by_cols(self, cols):
        """

        :param cols: The list of columns we are interested in

        :return: The resulted dataframe containing only the input columns
        """

        return self.quandl_data[cols]




