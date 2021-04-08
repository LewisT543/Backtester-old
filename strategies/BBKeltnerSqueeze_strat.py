import backtrader as bt
import backtrader.analyzers as btanalyzers
from class_params.AtrChans import CustomChannels
from class_params.KeltnerChans import KeltnerChannel


class BBKeltner(bt.Strategy):
    
    lines = ('squeeze',)
    params = (('period', 20), ('bbdev', 2.0), ('kcdev', 1.5),('movav', bt.ind.MovAv.Simple),)

    plotinfo = dict(subplot=True)
    

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        # If trade is open, nothing to be done
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT, GROSS: {trade.pnl}, NET: {trade.pnlcomm}')
    
    def notify_order(self, order):

        ### Checks on the status of the order ###

        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - nothing to be done.
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: {order.executed.price}, COST: {order.executed.value}, FEES: {order.executed.comm}')
                # Take note of buyprice + fees
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price}, COST: {order.executed.value}, FEES: {order.executed.comm}')
                self.sellprice = order.executed.price
                self.sellcomm = order.executed.comm
            
            # Take note of the bar at which the trade was closed
            self.bar_executed = len(self)

        # Catch failed order and log it
        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.log('Order Cancelled / Margin / Rejected')
        
        self.order = None

    def __init__(self):
        bol_bands = bt.ind.BollingerBands(
            period=self.p.period, devfactor=self.p.bbdev, movav=self.p.movav)
        kelt_chan = KeltnerChannel(
            period=self.p.period, devfactor=self.p.kcdev, movav=self.p.movav)
        self.l.squeeze = bol_bands.top - kelt_chan.top

    def next(self):

        ### TBC
        pass