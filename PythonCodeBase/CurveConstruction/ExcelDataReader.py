__author__ = 'Ray'

import xlrd

class ExcelDataReader(object):
    """
    Helper class that read market rate from file and
    store the date and rates into dictionary
    """
    def __init__(self, file_name):
        self._file_name = file_name

    def read_data_into_dictionary(self):
        """
        Read market rate from file and store the
        date and rates into dictionary
        :return:
        """
        wb = xlrd.open_workbook(self._file_name)

        sh1 = wb.sheet_by_index(0)
        sh2 = wb.sheet_by_index(1)

        #Store the valuation date
        self.value_date = sh1.cell(1, 1).value

        #Store the settlement date
        self.spot_date = sh1.cell(2, 1).value

        fields1 = ['rate', 'Spot_Date', 'Tenor']
        fields2 = ['rate', 'Fixing_Date', 'Tenor']

        #Store the market data into dictionary
        #self.libor = self.store_market_data(fields1, sh2, 2, 4, 4, 5, 6)
        self.libor = self.store_market_data(fields1, sh2, 2, 3, 4, 5, 6)

        tmp = self.store_market_data(fields1, sh2, 3, 4, 4, 5, 6)

        self.ed_future = self.store_market_data(fields2, sh2, 6, 14, 5, 6, 7)
        self.swap_rate = self.store_market_data(fields1, sh2, 16, 27, 4, 5, 6)
        self.fed_fund = self.store_market_data(fields1, sh2, 29, 30, 4, 5, 6)
        self.basis_swap_rate = self.store_market_data(fields1, sh2, 33, 49, 4, 5, 6)

        self.ed_future['rate'][0:0] = tmp['rate']
        self.ed_future['Fixing_Date'][0:0] = tmp['Spot_Date']
        self.ed_future['Tenor'][0:0] = tmp['Tenor']


    def store_market_data(self, fields, sh, from_row, to_row, *col):
        """
        Return the dictionary which store the date and rate info
        :param fields: The name we will use for the dictionary
        :param from_row: beginning row number in Excel
        :param to_row: ending row  number in Excel
        :param col: The list of column number in Excel
        :return: The dictionary that store the the date and rate for one market rate
        """
        values = [sh.col_values(x, from_row, to_row) for x in col]
        return dict(zip(fields, values))

