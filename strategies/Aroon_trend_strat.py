import backtrader as bt
import backtrader.analyzers as btanalyzers
from class_params.MyIchimoku import KijunSen
from class_params.AtrChans import CustomChannels

from datetime import datetime, timezone
import math


'''strategy_params = {
    'kijun_sen' : 26,
    'aroon' : 14,       
    'rsi' : 10,
    'atr' : 10,
    'atr_ma' : 10,
    'stoploss_atr' : 1.6,
    'take_profit' : 3.2,
    'risk' : 0.02
}'''



class Aroon(bt.Strategy):

    params = (
        ('kijun_sen', 26),
        ('aroon', 14),       
        ('rsi', 10),
        ('atr', 10),
        ('atr_ma', 10),
        ('stoploss_atr', 1.6),
        ('take_profit', 3.2),
        ('risk', 0.02),
        ('asset', 'BTCUSD'),
    )

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
        
        # keep note of orders, prices and commission
        self.order = None
        self.price = None
        self.comm = None
        self.order_direction = None
        # convenience
        self.dataclose = self.datas[0].close

        # Baseline >>>> Kijun-sen from Ichimoku cloud indicator
        self.baseline = KijunSen(self.data, period = self.params.kijun_sen, plotname = f'Kijun_sen {self.params.kijun_sen}')
            # Crossover returns 1 on close-price cross above and -1 on close-price cross below
        self.kijun_crossover = bt.ind.CrossOver(self.dataclose, self.baseline)

        # Confirmation 1 >>>> Aroon Up/Down 
        self.aroon_up_down = bt.ind.AroonUpDown(self.data, period = self.params.aroon, plotname = f'Aroon U+D {self.params.aroon}')
        # Background Indis - so I can still plot an AroonU+D
        self.aroon_up = bt.ind.AroonUp(self.data, period = self.params.aroon + 1, plot = False)
        self.aroon_down = bt.ind.AroonDown(self.data, period = self.params.aroon + 1, plot = False)
            # Linecross check - using bt.If() to compare line objects
        self.aroon_live = bt.If(self.aroon_up > self.aroon_down, 1,
            bt.If(self.aroon_up < self.aroon_down, -1, 0))

        # Confirmation 2 >>>> Relative Strength Index
        self.rsi = bt.ind.RelativeStrengthIndex(self.data, period = self.params.rsi, plotname = f'RSI {self.params.rsi}')
            # rsi_live will store +1 if it is above 50, and -1 if it is below or 0 if rsi == 50
        self.rsi_live = bt.If(self.rsi > 50, 1, bt.If(self.rsi < 50, -1, 0))

        # Volatility Indicator >>>> Average True Range and Simple Moving Average
        self.atr = bt.ind.AverageTrueRange(self.data,period = self.params.atr, plotname = f'ATR {self.params.atr}')
        self.atr_sma = bt.ind.MovingAverageSimple(self.atr, period = self.params.atr_ma, plotname = f'ATR_MA {self.params.atr_ma}')
            # if ATR > SMAofATR then we will store a 1, if ATR < SMAofATR then we store -1 if ATR=ATRSMA -> 0
        self.atr_rising = bt.If(self.atr > self.atr_sma, 1, bt.If(self.atr < self.atr_sma, -1, 0))
        
        # Custom Atr channels for exit param
        self.atr_chans = CustomChannels()
        
    def next(self):
        
        # Log closing price of each candle
        self.log(f'Close {self.dataclose[0]}')
        
        # Signals to be logged
        '''
        if self.aroon_live == 1:
            aroon_string = (f'Aroon Up > Aroon Down, ({round(self.aroon_up_down.up[0], 2)} > {round(self.aroon_up_down.down[0], 2)}) ')
        elif self.aroon_live == -1:
            aroon_string = (f'Aroon Down > Aroon Up, ({round(self.aroon_up_down.down[0], 2)} > {round(self.aroon_up_down.up[0], 2)}) ')
        else:
            aroon_string = ''    
        if self.rsi_live == 1:
            rsi_string = (f'RSI > 50 ({round(self.rsi[0], 2)}) ')
        elif self.rsi_live == -1:
            rsi_string = (f'RSI < 50 ({round(self.rsi[0], 2)}) ')
        else:
            rsi_string = ''     
        if self.atr_rising == 1:
            atr_string = (f'ATR > ATR_MA ({round(self.atr[0], 2)} > {round(self.atr_sma[0], 2)})')
        elif self.atr_rising == -1:
            atr_string = (f'ATR_MA > ATR ({round(self.atr_sma[0], 2)} > {round(self.atr[0], 2)})')
        else:
            atr_string = ''
        fullstring = aroon_string + rsi_string + atr_string
        self.log(f'Close {self.dataclose[0]} >>> {fullstring}')
        '''
        # Not in a trade currently, start checking for conditions to trade
        if not self.position:
            # Here begins the logic
            if (self.aroon_live == 1 and self.rsi_live == 1 and self.atr_rising == 1):
                self.log('GREENLIGHTS ON - WAITING FOR KIJUN UPCROSS')
                if self.kijun_crossover == 1:
                    # work out sizing, risk in cash / distance from price to SL
                    self.buy_size = (
                        (self.broker.cash * self.params.risk) / abs(self.dataclose[0] - self.atr_chans.lines.sllong[0])
                    )
                    self.log(f'BUY CREATED: {self.params.asset}, AMOUNT: {self.buy_size}, PRICE: {self.data.close[0]}')
                    self.log(f'STOPLOSS: {self.atr_chans.lines.sllong[0]}, TAKEPROFIT: {self.atr_chans.lines.tplong[0]}')
                    self.order = self.buy_bracket(
                        stopprice=self.atr_chans.lines.sllong[0],       # Stoploss order
                        price=self.dataclose,                           # MAIN order
                        limitprice=self.atr_chans.lines.tplong[0],      # Takeprofit order
                        size=self.buy_size,                             # Dynamic sizing based on acc / risk / width of SL
                        exectype=bt.Order.Market
                    )   # Returns a list of orders [main, stop, limit]
                    self.order_direction = 1
                    # saves a +1 if in a long
            
            if (self.aroon_live == -1 and self.rsi_live == -1 and self.atr_rising == 1):
                self.log('REDLIGHTS ON - WAITING FOR KIJUN DOWNCROSS')
                if self.kijun_crossover == -1 :
                    self.sell_size = (
                        (self.broker.cash * self.params.risk) / abs(self.dataclose[0] - self.atr_chans.lines.slshort[0])
                    )
                    self.log(f'SELL CREATED: {self.params.asset}, AMOUNT: {self.sell_size}, PRICE: {self.data.close[0]}')
                    self.log(f'STOPLOSS: {self.atr_chans.lines.slshort[0]}, TAKEPROFIT: {self.atr_chans.lines.tpshort[0]}')
                    self.order = self.sell_bracket(
                        stopprice=self.atr_chans.lines.slshort[0],      # Stoploss order
                        price=self.dataclose,                           # MAIN order
                        limitprice=self.atr_chans.lines.tpshort[0],     # Takeprofit order
                        size=self.sell_size,                            # Dynamic sizing based on acc / risk / width of SL
                        exectype=bt.Order.Market
                    )    # Use Zero here to select the MAIN order and save it to self.order
                    self.order_direction = -1
                    # Return a -1 if in a short
                        # Turns out I dont think I actually need to save direction because of order.close()

        elif self.position:
            if self.order_direction == 1:
                if self.kijun_crossover == -1:
                    self.close()
                    self.log('Long position closed due to kijun cross downwards')
            if self.order_direction == -1:
                if self.kijun_crossover == 1:
                    self.close()
                    self.log('Short position closed due to kijun cross upwards')