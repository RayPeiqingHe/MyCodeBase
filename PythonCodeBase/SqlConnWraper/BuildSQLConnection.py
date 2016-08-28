

def build_sql_conn(config_file, data_file=None):
    from ConfigParser import SafeConfigParser

    parser = SafeConfigParser()
    parser.read(config_file)

    bt_mode = parser.get('log_in', 'bt_mode')

    if bt_mode == 'mock':
        return build_test_conn(data_file)
    else:
        return build_prod_conn(config_file)


def build_test_conn(data_file=None):

    from SqlConnMock import SqlConnMock

    if data_file is None:
        data_file = '../SqlConnWraper/data/AAPL.csv'

    cxcn = SqlConnMock(data_file)

    return cxcn


def build_prod_conn(config_file):

    from ConnInfo import ConnInfo
    from PyMsSql import PyMsSql

    conn_info = ConnInfo(config_file)
    cxcn = PyMsSql(conn_info)

    return cxcn


if __name__ == '__main__':
    test_config = '../EventDrivenTradingSystem/config.ini'

    conn = build_sql_conn(test_config)

    with conn:
        df = conn.execute_query_as_df(None)

        df.set_index('datetime', inplace=True)

        print df
