import backtrader as bt
import backtrader.analyzers as btanalyzers

from datetime import datetime, timezone
import math

class GoldenCross3(bt.Strategy):

    params = (
        ('fast', 10),
        ('slow', 20),
        ('risk', 0.2),
        ('asset', 'BTCUSDT'),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        
        # Setting up variables
        self.order = None
        
        self.buyprice = None
        self.buycomm = None
        
        self.sellprice = None
        self.sellcomm = None
        
        self.dataclose = self.datas[0].close
        
        # Setting up Indicators
        self.fast_exp_mov_avg = bt.ind.ema.EMA(
            self.dataclose, period=self.params.fast,
            plotname=f'{self.params.fast} period EMA'
        )
        self.slow_exp_mov_avg = bt.ind.ema.EMA(
            self.dataclose, period=self.params.slow,
            plotname=f'{self.params.slow} period EMA'
        )
                
        self.crossover = bt.ind.CrossOver(self.fast_exp_mov_avg, self.slow_exp_mov_avg)
    
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

    def next(self):

        #log each close price
        self.log(f'Close, {self.dataclose[0]}')

        if not self.position and self.crossover > 0:
            self.buy_size = self.params.risk * self.broker.cash
            self.size = (self.buy_size / self.data.close)
            self.log(f'BUY CREATED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')
            self.order = self.buy(size=self.size)

        if not self.position and self.crossover < 0:
            self.sell_size = self.params.risk * self.broker.cash
            self.size = (self.sell_size / self.data.close)
            self.log(f'SELL CREATED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')
            self.order = self.sell(size=self.size)

        if self.position and self.crossover in [-1, 1]:
            self.close()