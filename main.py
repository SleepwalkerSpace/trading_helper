import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import backtrader as bt
import pandas as pd

from strategy.load_local_klines import load_local_klines
from strategy.strategy import MyStrategy


def main():
    # 1. 加载本地K线数据
    file_path = os.path.join(os.path.join(os.path.dirname(__file__)), 'data', 'BTCUSDT_1h.json')
    df = load_local_klines(file_path)
    if df is None:
        print("数据加载失败，请检查文件路径和格式")
        return
    
    # 2. 创建Backtrader引擎
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100.00) # 设置初始资金
    cerebro.broker.setcommission(commission=0.001) # 0.001即是0.1% 

    # 3. 添加数据
    data_feed = bt.feeds.PandasData(
            dataname=df,
            datetime=None,
            open='open',
            high='high',
            low='low',
            close='close',
            volume='volume'
        )
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(100000.0)  # 设置初始资金
    cerebro.broker.setcommission(commission=0.001)  # 设置交易佣金

    # 4. 添加策略（这里使用内置的买入持有策略作为示例）
    cerebro.addstrategy(MyStrategy)
    # 5. 运行回测
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    # 6. 绘制结果
    cerebro.plot(grid=False,voloverlay=False)

if __name__ == '__main__':
    main()
    