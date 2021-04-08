import backtrader as bt
from backtrader.indicators.basicops import Highest, Lowest

class KijunSen(bt.Indicator):
    
    lines = ('kijun_sen',)
    
    params = (
        ('period', 26),
    )

    plotinfo = dict(subplot=False)

    def __init__(self):

        hi_kijun = Highest(self.data.high, period=self.params.period)
        lo_kijun = Lowest(self.data.low, period=self.params.period)
        self.l.kijun_sen = (hi_kijun + lo_kijun) / 2.0


        super(KijunSen, self).__init__()
