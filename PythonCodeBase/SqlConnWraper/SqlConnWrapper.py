from __future__ import print_function
from abc import ABCMeta, abstractmethod
from ConnInfo import ConnInfo

class SqlConnWrapper(object):
    ''' class as the base Wrapper class for SQL data access

    Attributes
    ==========
    conn_str: string
        The connection string to the SQL data base

    Methods
    =======
    conn:
       Set up connection to the SQL data base
    execute_query:
       Execute a input sql query and return the result
    '''

    __metaclass__ = ABCMeta

    def __init__(self, conn_info):
        if not isinstance(conn_info, ConnInfo):
            raise TypeError('conn_info is not an object of ConnInfo')

        self.conn_info = conn_info

    @abstractmethod
    def execute_query(self, query):
        raise NotImplementedError("Should implement execute_query(query)")

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError("Should implement __enter__()")

    @abstractmethod
    def __exit__(self, type, value, traceback):
        raise NotImplementedError("Should implement __exit__(type, value, traceback)")

    @abstractmethod
    def execute_query_as_df(self, query):
        raise NotImplementedError("Should  execute_query_as_df(self, query)")

