__author__ = 'Ray'

import pandas as pd

def get_int_rate_info(loan_data_raw):
    '''

    :param loan_data:
    :return:
    '''

    cols = ['term','grade','sub_grade','int_rate']

    group_by_col = 'sub_grade'

    loan_data = loan_data_raw[cols]

    # Remove any 6% interest rate
    loan_data = loan_data[loan_data['int_rate'].str.strip() != '6.00%'].copy()

    loan_data['int_rate'] = loan_data['int_rate'].apply(lambda x: float(str(x).strip('%')) / 100)

    # Remove int rate smaller than A1 min int rate
    min_int_rate = loan_data[loan_data[group_by_col] == 'A1']['int_rate'].min()

    loan_data = loan_data[loan_data['int_rate'] >= min_int_rate]

    loan_data_36 = loan_data[loan_data['term'] == ' 36 months']

    df_36 = get_int_rate_info_term(loan_data_36)

    loan_data_60 = loan_data[loan_data['term'] == ' 60 months']

    df_60 = get_int_rate_info_term(loan_data_60)

    df_comb = df_36[['int_rate_min', 'int_rate_max', 'int_rate_low_bound']].copy()

    df_comb.columns = ['int_rate_min_36m', 'int_rate_max_36m', 'int_rate_lbound_36m']

    df_comb = df_comb.join(df_60[['int_rate_min', 'int_rate_max', 'int_rate_low_bound']])

    df_comb.columns = ['int_rate_min_36m', 'int_rate_max_36m', 'int_rate_lbound_36m',
                  'int_rate_min_60m', 'int_rate_max_60m', 'int_rate_lbound_60m']

    return df_comb


def get_int_rate_info_term(loan_data):
    '''

    :param loan_data:
    :return:
    '''

    g_loan_data = loan_data.groupby('sub_grade')

    df_loan_data = g_loan_data.min()

    df_loan_data.rename(columns={'int_rate' : 'int_rate_min'}, inplace=True)

    df_loan_data['int_rate_max'] = g_loan_data.max()['int_rate']

    df_loan_data['int_rate_low_bound'] = df_loan_data.shift(1)['int_rate_max']

    return df_loan_data





