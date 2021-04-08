from backtrader import feed    

class MyPandasData(feed.DataBase):    

    # Class for defining my Pandas data feed.

    lines = ('datetime', 'open', 'high', 'low', 'close', 'volume',)

    params = (
        ('datetime', 0),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', None),
    )