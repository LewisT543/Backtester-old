import backtrader as bt

class CustomChannels(bt.Indicator):

    lines = ('mid', 'slshort', 'sllong', 'tplong', 'tpshort')
    params = dict(
                ema=20,
                atr1=1.6,
                atr2=3.2,
                )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        mid=dict(ls='--'),  # dashed line
        slshort=dict(_samecolor=True),  # use same color as prev line (mid)
        sllong=dict(_samecolor=True),  # use same color as prev line (upper)
        tplong=dict(_samecolor=True),
        tpshort=dict(_samecolor=True),
    )

    def __init__(self):
        self.l.mid = bt.ind.EMA(self.data, period=self.p.ema)
        self.l.slshort = self.l.mid + (bt.ind.ATR(self.data, period=self.p.ema) * self.p.atr1)
        self.l.sllong = self.l.mid - (bt.ind.ATR(self.data, period=self.p.ema) * self.p.atr1)
        self.l.tplong = self.l.mid + (bt.ind.ATR(self.data, period=self.p.ema) * self.p.atr2)
        self.l.tpshort = self.l.mid - (bt.ind.ATR(self.data, period=self.p.ema) * self.p.atr2)