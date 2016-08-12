# PyMsSql.py

from SqlConnWrapper import SqlConnWrapper
import pymssql as mdb
import pandas as pd

class PyMsSql(SqlConnWrapper):
    ''' class as the base Wrapper class for SQL data access

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
    '''

    def __init__(self, conn_info):
        super(PyMsSql, self).__init__(conn_info)

    def __enter__(self):
        self.conn = mdb.connect(
            server=self.conn_info.db_host, user=self.conn_info.db_user,
            password=self.conn_info.db_pass, database=self.conn_info.db_name,
            autocommit=True
        )

        return self

    def __exit__(self, type, value, traceback):
        if self.conn is not None:
            self.conn.close()

    def execute_query(self, query):

        fail_cnt = 0

        while True:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(query)
                    data = cur.fetchall()

                return data
            except mdb.InterfaceError as e:
                fail_cnt += 1

                if fail_cnt > 10:
                    return None


    def execute_query_as_df(self, query):
        df = pd.read_sql(sql=query, con=self.conn, parse_dates=True)

        return df

