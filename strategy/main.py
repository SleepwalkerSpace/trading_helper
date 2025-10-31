import backtrader as bt
import pandas as pd
import yfinance as yf
import random  # 添加random库用于生成模拟数据

# 获取真实股票数据
def get_stock_data(symbol, start_date, end_date):
    """从yfinance获取股票数据"""
    data = yf.download(symbol, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    data['datetime'] = pd.to_datetime(data['Date'])
    data.set_index('datetime', inplace=True)
    return data

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

# 主程序
if __name__ == '__main__':
    # 创建引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(DoubleMAStrategy, fast_period=5, slow_period=20)
    
    # 获取数据（使用模拟数据避免网络问题）
    print("生成模拟数据...")
    
    # 创建更真实的模拟数据
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    base_price = 100
    prices = [base_price]
    
    for i in range(1, 500):
        # 模拟股价随机游走
        change = random.uniform(-2, 2)
        new_price = prices[-1] + change
        prices.append(max(new_price, 1))  # 确保价格不为负
    
    stock_data = pd.DataFrame({
        'datetime': dates,
        'open': [p + random.uniform(-1, 1) for p in prices],
        'high': [p + random.uniform(0, 2) for p in prices],
        'low': [p - random.uniform(0, 2) for p in prices],
        'close': prices,
        'volume': [random.randint(900000, 1100000) for _ in range(500)]
    })
    stock_data.set_index('datetime', inplace=True)
    
    data = bt.feeds.PandasData(dataname=stock_data)
    cerebro