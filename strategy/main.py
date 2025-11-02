import backtrader as bt
import pandas as pd

# 获取真实股票数据

# 定义双移动平均线策略
class DoubleMAStrategy(bt.Strategy):
    params = (
        ('fast_period', 5),   # 短期均线周期
        ('slow_period', 20),  # 长期均线周期
    )
    
    def __init__(self):
        # 创建移动平均线指标
        self.fast_ma = bt.indicators.SMA(
            self.datas[0], period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SMA(
            self.datas[0], period=self.params.slow_period
        )
        
        # 记录交易状态
        self.order = None
    
    def next(self):
        # 如果有未完成的订单，跳过
        if self.order:
            return
        
        # 如果没有持仓
        if not self.position:
            # 金叉：短期均线上穿长期均线，买入
            if self.fast_ma[0] > self.slow_ma[0] and self.fast_ma[-1] <= self.slow_ma[-1]:
                self.order = self.buy()
                print(f'买入信号: 日期={self.datas[0].datetime.date(0)}, '
                      f'价格={self.datas[0].close[0]:.2f}')
        
        # 如果持有仓位
        else:
            # 死叉：短期均线下穿长期均线，卖出
            if self.fast_ma[0] < self.slow_ma[0] and self.fast_ma[-1] >= self.slow_ma[-1]:
                self.order = self.sell()
                print(f'卖出信号: 日期={self.datas[0].datetime.date(0)}, '
                      f'价格={self.datas[0].close[0]:.2f}')