
import backtrader as bt

class KeltnerChannel(bt.Indicator):

    lines = ('mid', 'top', 'bot',)
    params = (('period', 20), ('devfactor', 1.5),
              ('movav', bt.ind.MovAv.Simple),)

    plotinfo = dict(subplot=False)
    plotlines = dict(
        mid=dict(ls='--'),
        top=dict(_samecolor=True),
        bot=dict(_samecolor=True),
    )

    def _plotlabel(self):
        plabels = [self.p.period, self.p.devfactor]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def __init__(self):
        self.lines.mid = ma = self.p.movav(self.data, period=self.p.period)
        atr = self.p.devfactor * bt.ind.ATR(self.data, period=self.p.period)
        self.lines.top = ma + atr
        self.lines.bot = ma - atr