import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import backtrader as bt
import pandas as pd

from strategy.load_local_klines import load_local_klines
from strategy.test_strategy import TestStrategy
from strategy.strategy import Strategy


def main():
    timeframes = [
        # "5m",
        # "15m",
        # "1h", 
        "4h",
    ]
    
    # 2. 创建Backtrader引擎
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.addobserver(bt.observers.Broker) 
    cerebro.addobserver(bt.observers.BuySell) 
    cerebro.broker.setcash(1000.0)  # 设置初始资金
    cerebro.broker.setcommission(commission=0.005)  # 设置交易佣金

    # 为每个时间框架加载并添加数据
    for i, timeframe in enumerate(timeframes):
        # 1. 加载本地K线数据
        file_name = 'BTCUSDT_' + timeframe + '.json'
        file_path = os.path.join(os.path.dirname(__file__), 'data', file_name)
        
        print(f"加载数据: {file_path}")
        df = load_local_klines(file_path)
        
        if df is None or df.empty:
            print(f"数据加载失败: {file_path}")
            continue
            
        # 检查数据基本信息
        print(f"{timeframe} 数据信息:")
        print(f"  时间范围: {df.index[0]} 到 {df.index[-1]}")
        print(f"  K线数量: {len(df)}")
        print(f"  价格范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
        print("---")
        
        # 确保datetime列是索引或存在datetime列
        if not isinstance(df.index, pd.DatetimeIndex):
            # 如果datetime不是索引，尝试转换
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
            else:
                print(f"错误: {timeframe} 数据没有datetime索引或列")
                continue
        
        # 创建PandasData，为每个数据源设置不同的名称
        data_feed = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # 使用索引作为datetime
            open='open',
            high='high', 
            low='low',
            close='close',
            volume='volume'
        )
        
        # 为数据源设置名称，方便在策略中识别
        data_feed._name = timeframe
        cerebro.adddata(data_feed, name=timeframe)

    # 4. 添加策略
    cerebro.addstrategy(Strategy)

    # 5. 运行回测
    print("初始资金: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("最终资金: %.2f" % cerebro.broker.getvalue())
    
    # 6. 绘制结果 - 调整参数避免重叠
    cerebro.plot(
        # style='candle',
        volume=True,
        grid=False,
    )

if __name__ == '__main__':
    main()