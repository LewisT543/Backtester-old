from backtrader.cerebro import OptReturn
import matplotlib
from datetime import datetime
import pandas as pd

from Data_getter import DataGetter
from strategies.Strategies import *
from strategies.Aroon_trend_strat import Aroon
from Storing_data_functions import timeframe_convert, create_dataframe, record_ta_data, add_sharpe_data, add_sqn_data, save_to_csv

import backtrader as bt


# Global variables for current study
start_cash = 10000
asset = 'BTCUSD'
timeframe = '1h'
exchange = 'Bitstamp'
fee_schedule = 0.001
sample_start = datetime(2019, 8, 1)
sample_end = datetime(2020, 8, 1)


strategy_params = {
    'kijun_sen' : 26,
    'aroon' : 14,       
    'rsi' : 10,
    'atr' : 10,
    'atr_ma' : 10,
    'stoploss_atr' : 1.6,
    'take_profit' : 3.2,
    'risk' : 0.02
}

if __name__ == '__main__':
    # Setting up the dataframe to supply the feed and the feed itself
    dr1 = DataGetter(ticker=asset, timeframe=timeframe, exchange=exchange)
    data_1 = dr1.data_to_df()
    dataframe = dr1.select_data(data_1, keyword='ohlc+vol')
    print(dataframe)
    
    # Sort out compression and bt.TimeFrame for the data feed
    paramsdict = timeframe_convert(timeframe)
    print(str(paramsdict['timeframe']), str(paramsdict['compression']))
    datastream = bt.feeds.PandasData(
        dataname = dataframe,
        timeframe = paramsdict['timeframe'],
        compression = paramsdict['compression'],
        datetime = 0, 
        open = 2, 
        high = 3, 
        low = 4, 
        close = 5,
        volume = 6,
        fromdate = sample_start,
        todate = sample_end
    )

    ### Cerebro setup ###
        # Instantiate Cerebro and get it all set up
    cerebro = bt.Cerebro(optreturn=False)
        # Optimise the strat
    #cerebro.optstrategy(GoldenCross3, fast=13, slow=range(20, 25))
    '''cerebro.optstrategy(Aroon, 
        kijun_sen=strategy_params['kijun_sen'],
        aroon=strategy_params['aroon'],
        rsi=strategy_params['rsi'],
        atr=strategy_params['atr'],
        atr_ma=strategy_params['atr_ma'],
        stoploss_atr=strategy_params['stoploss_atr'],
        take_profit=strategy_params['take_profit'],
        risk=strategy_params['risk']
    )'''
    cerebro.optstrategy(KijunTest,
        kijun=20,
        atr=14,
        atr_ema=5
    )
    cerebro.adddata(datastream)
        # Setup the broker    
    cerebro.broker.setcash(start_cash)
    cerebro.broker.setcommission(commission=fee_schedule, leverage=50)
        # Add Analyzers
    cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name = 'ta')
    cerebro.addanalyzer(btanalyzers.SQN, _name = 'sqn')
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name = 'sharperatio')
    cerebro.addanalyzer(btanalyzers.Transactions, _name = 'transac')

    ### Cerebro run ###
        # Find start value
    start_portfolio_value = round(cerebro.broker.getvalue(), 2)
    print(f'Starting Portfolio Value: {start_portfolio_value}')
        # Run sctrategy  
    opt_runs = cerebro.run()

    #results_df = pd.read_csv('data\\results\\backtesting_results.csv', index_col=0, parse_dates=['start_date', 'end_date'])

    for run in opt_runs:
       
        for strategy in run:
            
            strat_strings = (str(strategy).split('.', 2))
            strat_name = strat_strings[0][1:]
            parameters = strategy.params._getitems() 
            # parameters = strategy.params._getitems() >>>> works for single runs, but not OptStrats
            todays_datetime = datetime.now()
            dt_string = todays_datetime.strftime('%Y-%m-%d %H:%M:%S')

            df = create_dataframe(sample_start, sample_end, strat_name, str(parameters), asset)
            df = record_ta_data(strategy.analyzers.ta.get_analysis(), df, start_cash)
            df = add_sqn_data(strategy.analyzers.sqn.get_analysis(), df)
            df = add_sharpe_data(strategy.analyzers.sharperatio.get_analysis(), df)
            save_to_csv(df)
    cerebro.plot(style='candlestick')



