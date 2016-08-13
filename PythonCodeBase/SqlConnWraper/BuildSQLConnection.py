

def build_sql_conn(config_file):
    from ConfigParser import SafeConfigParser

    parser = SafeConfigParser()
    parser.read(config_file)

    bt_mode = parser.get('log_in', 'bt_mode')

    if bt_mode == 'mock':
        return build_test_conn()
    else:
        return build_prod_conn(config_file)

def build_test_conn():

    from SqlConnMock import SqlConnMock

    cxcn = SqlConnMock('../SqlConnWraper/data/AAPL.csv')

    return cxcn

def build_prod_conn(config_file):

    from ConnInfo import ConnInfo
    from PyMsSql import PyMsSql

    conn_info = ConnInfo(config_file)
    cxcn = PyMsSql(conn_info)

    return cxcn

if __name__ == '__main__':
    config_file = '../EventDrivenTradingSystem/config.ini'

    conn = build_sql_conn(config_file)

    with conn:
        df = conn.execute_query_as_df(None)

        df.set_index('datetime', inplace=True)

        print df