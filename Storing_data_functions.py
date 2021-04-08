import pandas as pd
import backtrader as bt
from datetime import datetime
import mysql.connector
import numpy as np

def timeframe_convert(string):
    ret_dict = {}
    if string == 'minute':
        ret_dict['timeframe'] = bt.TimeFrame.Minutes
        ret_dict['compression'] = 1
    if string == '1h':
        ret_dict['timeframe'] = bt.TimeFrame.Minutes
        ret_dict['compression'] = 60
    if string == 'd':
        ret_dict['timeframe'] = bt.TimeFrame.Days
        ret_dict['compression'] = 1
    return ret_dict

def pnl_calc(start_val, end_val):
    pnl = end_val - start_val
    if pnl > 0:
        pct_change = ((end_val - start_val) / start_val) * 100
    elif pnl < 0:
        pct_change = ((start_val - end_val) / start_val) * -100
    else:
        pct_change = 0
    return round(pct_change, 2)

def create_dataframe(start_date, end_date, strat_name, param_str, asset):
    # Create the dataframe for other results to be added to
    sample_length = end_date - start_date
    todays_datetime = datetime.now()
    dt_string = todays_datetime.strftime('%Y-%m-%d %H:%M:%S')

    dataframe = pd.DataFrame(
        {
        'test_date' : [dt_string],
        'asset' : [asset],
        'strategy' : [strat_name],
        'strat_params' : [param_str],
        'start_date' : [start_date],
        'end_date' : [end_date],
        'sample_length' : [sample_length],
        },
        columns = ['test_date','asset', 'strategy', 'strat_params', 'start_date', 'end_date', 'sample_length']
    )
    return dataframe

def record_ta_data(analyzer, dataframe, start_cash):
    ### Get the data required from analyzer object ###
    # Absolute joke of a function. Why would you make a new data-type just to store trade analysis results. 
        # Thanks Auto-Dictionary, you are the reason for these try/excepts.
    try:
        total_open = analyzer.total.open
    except:
        total_open = 0    
    
    try:
        total_closed = analyzer.total.closed
    except:
        total_closed = 0    
    
    try:
        total_won = analyzer.won.total
    except:
        total_won = 0
    
    try:
        total_lost = analyzer.lost.total
    except:
        total_lost = 0
    
    try:
        win_streak = analyzer.streak.won.longest
    except:
        win_streak = 0
    
    try:
        loss_streak = analyzer.streak.lost.longest
    except:
        loss_streak = 0
        
    try:
        pnl_net = analyzer.pnl.net.total
    except:
        pnl_net = 0
    
    try:
        strike_rate = (total_won / total_closed) * 100
    except:
        strike_rate = 0
    
    end_cash = pnl_net + start_cash
    pct_change = pnl_calc(start_cash, end_cash)
    
    
    ta_df = pd.DataFrame(
        {
        'total_open' : [total_open],
        'total_closed' : [total_closed],
        'total_won' : [total_won],
        'total_lost' : [total_lost],
        'win_streak' : [win_streak],
        'lose_streak' : [loss_streak],
        'pnl_net' : [round(pnl_net, 2)],
        'pct_change' : [round(pct_change, 2)],
        'strike_rate' : [round(strike_rate, 2)]
        },
        columns = ['total_open', 'total_closed', 'total_won', 'total_lost', 
        'win_streak', 'lose_streak', 'pnl_net', 'pct_change', 'strike_rate'],
    )
    frames = [dataframe, ta_df]
    df = pd.concat(frames, axis=1)
    return(df)

def add_sqn_data(analyzer, dataframe):
    ### Add the SQN as new column in pandas DF
    sqn_df = pd.DataFrame(
        {
        'sqn' : [round(analyzer.sqn, 2)]
        },
        columns = ['sqn']
    )
    frames = [dataframe, sqn_df]
    df = pd.concat(frames, axis=1)
    return(df)

def add_sharpe_data(analyzer, dataframe):
    ### Add sharpe ratio as new column in pandas DF
    try:
        sharpe_r = round(analyzer.get('sharperatio'), 2)
    except:
        sharpe_r = 0

    sharpe_df = pd.DataFrame(
        {
        'sharpe_ratio' : [sharpe_r],
        },
        columns = ['sharpe_ratio']
    )
    frames = [dataframe, sharpe_df]
    df = pd.concat(frames, axis=1)
    return(df)


def save_to_csv(new_df):
    # Save the data to CSV
        # creates a new file if none present
        # Merges both old and new dataframes (deleting duplicates) before saving to CSV
    try:
        base_df = pd.read_csv('data\\results\\backtesting_results.csv', index_col=0, parse_dates=['start_date', 'end_date'])        
        frames = [base_df, new_df]
        df = pd.concat(frames)    
        print('Updated file contents.\nSaved to: >> data\\results\\backtesting_results.csv) <<')
        df.to_csv('data\\results\\backtesting_results.csv', mode='w')

    except:
        print('Filename not found, new file will be created called: "backtesting_results.csv" in local "results" folder.')
        new_df.to_csv('data\\results\\backtesting_results.csv', mode='w')
    


'''
def save_to_database(database_name, dataframe):
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='lewis1997'
    )
    mycursor = mydb.cursor()
    mycursor.execute('SHOW DATABASES')
    if database_name not in mycursor:
        mycursor.execute(f'CREATE DATABASE {database_name}')

    mycursor.execute('SHOW TABLES')
    if 'backtest_results' not in mycursor:
        mycursor.execute(f'CREATE TABLE backtest_results (
            Record_ID INT,
            test_date DATETIME,
            asset VARCHAR(255),
            strategy VARCHAR(255),
            strat_params VARCHAR(255),
            start_date DATETIME,
            end_date DATETIME,
            sample_length
            )'
        )'''

    