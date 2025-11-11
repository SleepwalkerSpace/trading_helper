import backtrader as bt
import backtrader.indicators as btind
from enum import Enum

class IndicatorType(Enum):
    """指标类型枚举"""
    EMA_20 = "EMA_20"
    EMA_200 = "EMA_200"
    BOLL_200 = "BOLL_200"
    RSI_EMA = "RSI_EMA"

class StrategyOverbought(bt.Strategy):
    """
    策略-上涨趋势时超买
    """
    
    def __init__(self):
        self.trade_count = 0

        # 各个时间框架的指标
        self.timeframe_indicators = {}
        for i in range(len(self.datas)):
            self.timeframe_indicators[i] = {
                IndicatorType.EMA_20: btind.ExponentialMovingAverage(self.datas[i], period=14),
                IndicatorType.EMA_200: btind.ExponentialMovingAverage(self.datas[i], period=200),
                IndicatorType.BOLL_200: btind.BollingerBands(self.datas[i], period=200),
                IndicatorType.RSI_EMA: btind.RSI_EMA(self.datas[i], period=14, upperband=80, lowerband=30, plot=True),
            }
        
        self.order = None
    
    def are_indicators_ready(self, data_index):
        """检查指标是否已计算完成(避免使用NaN值)"""
        ind = self.indicators[data_index]
        # 检查是否有足够的数据计算指标
        conditions = [
            not bt.math.isnan(ind[IndicatorType.EMA_20][0]),
            not bt.math.isnan(ind[IndicatorType.EMA_200][0]),
            not bt.math.isnan(ind[IndicatorType.BOLL_200].top[0]),
            not bt.math.isnan(ind[IndicatorType.BOLL_200].mid[0]),
            not bt.math.isnan(ind[IndicatorType.BOLL_200].bot[0]),
            not bt.math.isnan(ind[IndicatorType.RSI_EMA][0]),
        ]
        return all(conditions)

    def get_current_price(self, data_index:int):
        return self.datas[data_index].close[0]
    
    def is_short_signal(self):
        """是否满足做空信号"""
        current_price_0 = self.get_current_price(0)
        current_price_1 = self.get_current_price(1)

        # 小时间级别指标
        current_inds_0 = self.timeframe_indicators[0]
        conditions_0 = [
            current_price_0 > current_inds_0[IndicatorType.EMA_20],
            current_inds_0[IndicatorType.EMA_20] > current_inds_0[IndicatorType.EMA_200],
            current_inds_0[IndicatorType.EMA_20] > current_inds_0[IndicatorType.BOLL_200].top[0],
            current_inds_0[IndicatorType.EMA_200] > current_inds_0[IndicatorType.BOLL_200].mid[0],
            current_inds_0[IndicatorType.RSI_EMA][-1] >= 80,
        ]
        if all(conditions_0):
            print("conditions_0", 
                  current_inds_0[IndicatorType.RSI_EMA][-2],">>",
                  current_inds_0[IndicatorType.RSI_EMA][-1],">>",
                  current_inds_0[IndicatorType.RSI_EMA][0])         

        if not all(conditions_0):
            return
        
        # 大时间级别指标
        current_inds_1 = self.timeframe_indicators[1]
        conditions_1 = [
            current_price_1 > current_inds_1[IndicatorType.EMA_20],
            current_inds_1[IndicatorType.EMA_20] > current_inds_1[IndicatorType.EMA_200],
            current_inds_1[IndicatorType.EMA_200] > current_inds_1[IndicatorType.BOLL_200].mid[0],
            # current_price_1 >= current_inds_1[IndicatorType.BOLL_200].top[0],
            current_inds_1[IndicatorType.RSI_EMA][-1] >= 80,
        ]
        print(conditions_1, all(conditions_1),  current_price_1 ,current_inds_1[IndicatorType.BOLL_200].top[0],)
        
        return all(conditions_0) and not all(conditions_1)

    def is_exit_signal(self):
        """是否平仓"""
        current_price = self.datas[0]
        current_inds = self.timeframe_indicators[0]
        conditions = [
            current_price <= current_inds[IndicatorType.BOLL_200].bot[0]
        ]
        return all(conditions)

    def next(self):

        if self.position and self.position.size < 0:  # 持有空单
            if self.is_exit_signal():
                self.close(data=self.datas[0])

        else:
            if self.is_short_signal():
                if self.trade_count > 3:
                    return
                self.sell(data=self.datas[0], size=0.2)
                self.trade_count += 1