# SqlConnMock

from SqlConnWrapper import SqlConnWrapper
import pandas as pd
import csv


class SqlConnMock(SqlConnWrapper):
    """ class as the base Wrapper class for SQL data access

    Attributes
    ==========
    conn_str: string
        The connection string to the SQL data base

    Methods
    =======
    execute_query:
       Execute a input sql query and return the result
    execute_query_as_df:
       Execute a input sql query and return a Pandas data frame
    """

    def __init__(self, file_name):

        self.data_file = file_name

    def __enter__(self):
        self.file = open(self.data_file)

        return self

    def __exit__(self, obj_type, value, traceback):
        if self.file is not None:
            self.file.close()

    def execute_query(self, query):
        data = []

        spamreader = csv.reader(self.file, delimiter=' ', quotechar='|')

        for row in spamreader:
            data.append(row)

        return data

    def execute_query_as_df(self, query):
        result = pd.read_csv(self.file)

        return result


if __name__ == '__main__':
    with SqlConnMock('data/test.csv') as sql_mock:
        df = sql_mock.execute_query_as_df(None)

        df.set_index('datetime', inplace=True)

        df.index = pd.to_datetime(df.index)

        print df
