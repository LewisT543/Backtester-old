from class_params.MyIchimoku import KijunSen
from class_params.AtrChans import CustomChannels
import backtrader as bt
import backtrader.analyzers as btanalyzers

from datetime import datetime, timezone
import math


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # Pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None

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
            
            # Take note of the bar at which the trade was closed
            self.bar_executed = len(self)

        # Catch failed order and log it
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Cancelled/Margin/Rejected')
        
        # no pending order
        self.order = None
        
    def notify_trade(self, trade):
        # If trade is open, nothing to be done
        if not trade.isclosed:
            return

        self.log(f'OPERATION PROFIT, GROSS: {trade.pnl}, NET: {trade.pnlcomm}')
        

    def next(self):

        ################# This is the part of the program responsible for the Strategy ###################

        # Simply log the closing price of the series from the reference
        self.log(f'Close, {self.dataclose[0]}')

        # Are we in the market?
        if not self.position:

            # current close less than previous close
            if self.dataclose[0] < self.dataclose[-1]:
                
                # previous close less than the previous close
                if self.dataclose[-1] < self.dataclose[-2]:
                    
                    # BUY (with all possible default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()
        
        # Already got a position open, sell maybe
        else:
            if len(self) >= (self.bar_executed + 5):
                # SELL
                self.log(f'SELL CREATE, {self.dataclose[0]}')

                # Record the order, stops double selling
                self.order = self.sell()


class GoldenCross(bt.Strategy):

    params = (
        ('fast', 10),
        ('slow', 20),
        ('long_term', 50),
        ('risk', 0.05),
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
        self.dataclose = self.datas[0].close
        
        # Setting up Indicators
        self.fast_exp_mov_avg = bt.ind.ema.EMA(
            self.data.close, period=self.params.fast,
            plotname=f'{self.params.fast} day EMA'
        )
        self.slow_exp_mov_avg = bt.ind.ema.EMA(
            self.data.close, period=self.params.slow,
            plotname=f'{self.params.slow} day EMA'
        )
        self.long_term_exp_mov_avg = bt.ind.ema.EMA(
            self.data.close, period=self.params.long_term,
            plotname=f'{self.params.long_term} day EMA'
        )
        self.crossover = bt.ind.CrossOver(self.fast_exp_mov_avg, self.slow_exp_mov_avg)

    def next(self):
        # This contains the golden cross logic
        self.log(f'Close, {self.dataclose[0]}')
        if self.position.size == 0:
            if self.crossover > 0:
                self.buy_size = (self.params.risk * self.broker.cash)
                self.size = (self.buy_size / self.data.close)

                self.log(f'BUY CREATED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')
                
                # Execute the buy
                self.order = self.buy(size=self.size)

        if self.position.size > 0:
            if self.crossover < 0:
                self.log(f'SELL CREATED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')

                # close the order
                self.order = self.sell(size=self.size)

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
            
            # Take note of the bar at which the trade was closed
            self.bar_executed = len(self)

        # Catch failed order and log it
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Cancelled/Margin/Rejected')

        self.order = None

class GoldenCross2(bt.Strategy):

    params = (
        ('fast', 10),
        ('slow', 20),
        ('long_term', 50),
        ('risk', 0.05),
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
            self.data.close, period=self.params.fast,
            plotname=f'{self.params.fast} day EMA'
        )
        self.slow_exp_mov_avg = bt.ind.ema.EMA(
            self.data.close, period=self.params.slow,
            plotname=f'{self.params.slow} day EMA'
        )
        self.long_term_exp_mov_avg = bt.ind.ema.EMA(
            self.data.close, period=self.params.long_term,
            plotname=f'{self.params.long_term} day EMA'
        )
        
        self.crossover = bt.ind.CrossOver(self.fast_exp_mov_avg, self.slow_exp_mov_avg)

    def next(self):
        
        ### The New and improved golden cross (2 EMA strat), now with shorting too ###

        self.log(f'Close, {self.dataclose[0]}')

        # if self.position.size == 0, no position is opened, so we look to open one
        if self.position.size == 0:
            if self.crossover > 0:
                self.buy_size = self.params.risk * self.broker.cash
                self.size = (self.buy_size / self.data.close)
                self.log(f'BUY CREATED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')
                
                self.order = self.buy(size=self.size)

            if self.crossover < 0:
                self.sell_size = self.params.risk * self.broker.cash
                self.size = self.sell_size / self.data.close
                self.log(f'SELL CREATED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')

                self.order = self.sell(size=self.size)

        # if we have a position, we will look to close it on a cross
        
        if self.position.size > 0:
            if self.crossover < 0:
                self.log(f'BUY CLOSED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')
                
                self.order = self.sell(size=self.position.size)

            if self.crossover > 0:
                self.log(f'SELL CLOSED: {self.params.asset}, AMOUNT: {self.size}, PRICE: {self.data.close[0]}')

                self.order = self.buy(size=self.position.size)


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
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Cancelled / Margin / Rejected')
        
        self.order = None

class KijunTest(bt.Strategy):

    params = (('kijun', 26),('atr', 10), ('atr_ema', 5), ('rsi', 20), ('risk', 0.02), ('exit_atr', 20), )

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
                self.log(f'BUY EXECUTED: {round(order.executed.price, 4)}, COST: {round(order.executed.value, 4)}, FEES: {round(order.executed.comm, 4)}')
                # Take note of buyprice + fees
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
            elif order.issell():
                self.log(f'SELL EXECUTED, {round(order.executed.price, 4)}, COST: {round(order.executed.value, 4)}, FEES: {round(order.executed.comm, 4)}')
                self.sellprice = order.executed.price
                self.sellcomm = order.executed.comm
            
            # Take note of the bar at which the trade was closed
            self.bar_executed = len(self)

        # Catch failed order and log it
        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.log('Order Cancelled / Margin / Rejected')
        
        self.order = None

    def __init__(self):
        self.dataclose = self.datas[0].close
        # Kijun sen line and price cross
        self.l.kijun = KijunSen(self.data, period=self.p.kijun, plotname=f'Kijun-Sen {self.p.kijun}')
        self.kijun_cross = bt.ind.CrossOver(self.dataclose, self.l.kijun, plotname=f'Price X Kijun')
        # atr and atr_ema and their crossover
        self.atr = bt.ind.ATR(self.data, period=self.p.atr, plotname=f'ATR {self.p.atr}')
        self.atr_ema = bt.ind.EMA(self.atr, period=self.p.atr_ema, plotname=f'ATR_EMA {self.p.atr_ema}') 
        self.atr_rising = bt.If(self.atr > self.atr_ema, 1, bt.If(self.atr < self.atr_ema, -1, 0))
        # custom atr channels
        self.channels = CustomChannels(ema=self.p.exit_atr)
        # rsi 
        self.rsi = bt.ind.RSI(self.data, period=self.p.rsi, plotname=f'RSI {self.p.rsi}')
        

    def next(self):
        
        if not self.position:
            if self.kijun_cross == 1 and self.atr_rising == 1 and self.rsi > 50:
                risk_allowance = self.broker.cash * self.params.risk
                stoploss_price = self.channels.l.sllong[0]
                target_price = self.channels.l.tplong[0]
                position_size = risk_allowance / (self.dataclose[0] - self.channels.l.sllong[0])
                self.log(f'risk_allowance: {risk_allowance}, dataclose[0]: {self.dataclose[0]}, stop_channel[0]: {self.channels.l.sllong[0]}, pos_size: {position_size} ')
                self.buy_bracket(limitprice=target_price, price=self.dataclose[0], stopprice=stoploss_price, size=position_size)
                self.log(f'BUY created - PRICE: {round(self.dataclose[0], 4)} - TARGET {round(target_price, 4)} - STOP {round(stoploss_price, 4)}')    
                
        if not self.position:
            if self.kijun_cross == -1 and self.atr_rising == 1 and self.rsi < 50:
                risk_allowance = self.broker.cash * self.params.risk
                stoploss_price = self.channels.l.slshort[0]
                target_price = self.channels.l.tpshort[0]
                position_size = risk_allowance / (self.dataclose[0] - self.channels.l.slshort[0])   
                self.log(f'risk_allowance: {risk_allowance}, dataclose[0]: {self.dataclose[0]}, stop_channel[0]: {self.channels.l.slshort[0]}, pos_size: {position_size} ')
                self.buy_bracket(limitprice=target_price, price=self.dataclose[0], stopprice=stoploss_price, size=position_size)
                self.log(f'SELL created - PRICE: {round(self.dataclose[0], 4)} - TARGET {round(target_price, 4)} - STOP {round(stoploss_price, 4)}')