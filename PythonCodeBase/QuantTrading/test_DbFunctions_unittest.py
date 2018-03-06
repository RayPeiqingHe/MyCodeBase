import unittest
from price_retrieval import get_daily_historic_data_pandas
from price_retrieval import insert_daily_data_into_db_from_df
import datetime


class TestDbFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_prices(self):
        ticker = 'F'

        start_date = datetime.date(2018, 1, 8)

        end_date = datetime.date(2018, 1, 12)

        df_prices = get_daily_historic_data_pandas(ticker, start_date, end_date, 'yahoo')

        print df_prices

        self.assertEqual(len(df_prices.index), 5)

    def test_insert_prices(self):

        ticker = 'F'

        start_date = datetime.date(2018, 1, 8)

        end_date = datetime.date(2018, 1, 12)

        df_prices = get_daily_historic_data_pandas(ticker, start_date, end_date, 'yahoo')

        table_name = 'daily_price_dev'

        try:
            insert_daily_data_into_db_from_df(df_prices, ticker, table_name)
        except Exception as ex:
            print ex

            self.fail('Insert daily price fail')


if __name__ == '__main__':
    unittest.main()
