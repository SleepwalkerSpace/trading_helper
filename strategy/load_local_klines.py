import json
import pandas as pd
from datetime import datetime

def load_local_klines(file_path: str):
    """
    加载您的Binance JSON数据文件
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        kline_data = json.load(f)
        print(f"成功加载 {len(kline_data)} 条K线数据")
        
        # 转换为pandas DataFrame
        data_list = []
        
        for i, kline in enumerate(kline_data):
            # if i == 1000:
            #     break
            try:
                dt = datetime.fromtimestamp(kline['openTime'] / 1000)
                # 转换数据类型（字符串转浮点数）
                data_list.append({
                    'datetime': dt,
                    'open': float(kline['open']),
                    'high': float(kline['high']),
                    'low': float(kline['low']),
                    'close': float(kline['close']),
                    'volume': float(kline['volume']),
                    'openinterest': 0,
                    # 保留额外信息
                    'quote_volume': float(kline['quoteAssetVolume']),
                    'trades': kline['numberOfTrades'],
                    'taker_buy_volume': float(kline['takerBuyBaseAssetVolume']),
                    'taker_sell_volume': float(kline['takerSellBaseAssetVolume']),
                    # 'buy_ratio': float(kline['buyRatio']),
                    # 'sell_ratio': float(kline['sellRatio'])
                })
                
            except Exception as e:
                print(f"跳过第{i}条数据错误: {e}")
                continue
        
        if not data_list:
            raise ValueError("没有有效数据可处理")
        
        # 创建DataFrame
        df = pd.DataFrame(data_list)
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)  # 按时间排序
        
        # 打印数据信息
        print(f"有效数据条数: {len(df)}")
        print(f"时间范围: {df.index[0]} 到 {df.index[-1]}")
        print(f"价格范围: {df['low'].min():.2f} - {df['high'].max():.2f}")
        print(f"总成交量: {df['volume'].sum():.2f}")
        
        return df
        