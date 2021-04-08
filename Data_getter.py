import pandas as pd
import datetime

### Data from:                                      ###
### http://www.cryptodatadownload.com/data/ ###



class DataGetter:

    ### Class responsible for opening local csv files and representing the data in a pandas dataframe ###

    def __init__(self, ticker, timeframe, exchange='Binance'):
        self.ticker = ticker
        self.timeframe = timeframe
        self.exchange = exchange
        
    def data_to_df(self):

        ### retrieves the data from local CSV folders and returns a pandas DF ###        
        # Retrieve the CSV
        csv_df = pd.read_csv(f'data\\{self.timeframe}\\{self.exchange}_{self.ticker}_{self.timeframe}.csv'
                            , parse_dates=['unix'])
        csv_df.drop(columns=['Unnamed: 0'], inplace=True) 
        # iloc[::-1] reverses all data, so we have latest data at the 'bottom'
        csv_df = csv_df.iloc[::-1]
        return csv_df

    def select_data(self, dataframe, keyword='close'):

        # takes in a dataframe and returns an edited one based on keyword requirements
        
        pair = self.ticker.split('U', 1)    # remove asset from trading pair                   
        market = 'U' + pair[1]              # example: LINKUSDT -> LINK
                                            # returns 'U' + SD or SDT depending on tether or not           
                                            
        if keyword == 'close':
            dataframe = dataframe.drop(columns=['open', 'high', 'low', f'Volume {market}'])
            print('Dataframe returned with Close format')
        elif keyword == 'close+vol':
            dataframe = dataframe.drop(columns=['open', 'high', 'low'])
            print('Dataframe returned with Close-Vol format')
        elif keyword == 'ohlc':            
            dataframe = dataframe.drop(columns=[f'Volume {market}'])
            print('Dataframe returned with OHLC format')
        elif keyword == 'ohlc+vol':            
            print('Dataframe returned with OHLC+Vol format')
        else:
            print('Incorrect keyword, dataframe returned unchanged')

        return dataframe






