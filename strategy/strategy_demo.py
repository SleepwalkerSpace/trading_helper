import backtrader as bt
import backtrader.indicators as btind

from strategy.common import IndicatorType, SignalType


class StrategyDemo(bt.Strategy):
    """
    策略-上涨趋势时超卖
    """

    def __init__(self):
        # 交易次数初始化为0
        self.trade_count = 0
        # 超买阈值
        self.overbought_threshold = 70
        self.is_overbought = False
        # 超买阈值
        self.oversold_threshold = 30
        self.is_oversold = False
        # 
        self.volumes = []

        # 各个时间框架的指标
        self.timeframe_indicators = {}
        for i in range(len(self.datas)): 
            self.timeframe_indicators[i] = {
                # IndicatorType.EMA_20: btind.ExponentialMovingAverage(self.datas[i], period=20),
                # IndicatorType.EMA_200: btind.ExponentialMovingAverage(self.datas[i], period=200),
                IndicatorType.BOLL_200: btind.BollingerBands(self.datas[i], period=14),
                IndicatorType.RSI_EMA: btind.RSI_EMA(self.datas[i], period=14, upperband=70, lowerband=30, plot=True),
            }
    
    def are_indicators_ready(self, data_index):
        """检查指标是否已计算完成(避免使用NaN值)"""
        ind = self.indicators[data_index]
        # 检查是否有足够的数据计算指标
        conditions = [
            # not bt.math.isnan(ind[IndicatorType.EMA_20][0]),
            # not bt.math.isnan(ind[IndicatorType.EMA_200][0]),
            not bt.math.isnan(ind[IndicatorType.BOLL_200].top[0]),
            not bt.math.isnan(ind[IndicatorType.BOLL_200].mid[0]),
            not bt.math.isnan(ind[IndicatorType.BOLL_200].bot[0]),
            not bt.math.isnan(ind[IndicatorType.RSI_EMA][0]),
        ]
        return all(conditions)

    def get_current_price(self, data_index:int):
        """获取当前价格"""
        return self.datas[data_index].close[0]

    def get_current_indicators(self, data_index:int):
        """获取当前指标"""
        return self.timeframe_indicators[data_index]
    
    def sigle(self) -> SignalType:
        """交易信号"""
        current_price_0 = self.get_current_price(0)
        current_inds_0 = self.get_current_indicators(0)

        buy_conditions = [
            current_price_0 > current_inds_0[IndicatorType.BOLL_200].top,
            current_inds_0[IndicatorType.RSI_EMA].rsi >= 70,
        ]
        return SignalType.SELL if all(buy_conditions) else None

    def next(self):
        before_avg_volume_14 = 0
        if len(self.volumes) >= 14:
            before_avg_volume_14 = sum(self.volumes[-14:]) / 14
        current_volume = self.datas[0].volume[0]
        self.volumes.append(current_volume)

        if self.is_overbought:
            if self.get_current_indicators(0)[IndicatorType.RSI_EMA].rsi < self.overbought_threshold:
                self.is_overbought = False
                # print("超买结束: ", self.get_current_price(0), self.broker.getvalue())

        # 持有仓位
        if self.position:
            # 做空仓位
            if self.position.size < 0:
                if self.get_current_indicators(0)[IndicatorType.RSI_EMA].rsi <= 35 or self.get_current_price(0) <= self.get_current_indicators(0)[IndicatorType.BOLL_200].bot:
                    self.close(data=self.datas[0])
                    print("平仓 - 止盈: ", self.get_current_price(0), self.broker.getvalue())

                else:
                    open_price = self.position.price
                    curr_price = self.position.adjbase
                    if curr_price > open_price: 
                        if self.get_current_indicators(0)[IndicatorType.RSI_EMA].rsi >= 70 and self.is_overbought == False:
                            if curr_price > self.get_current_indicators(0)[IndicatorType.BOLL_200].top:
                                self.close(data=self.datas[0])
                                self.is_overbought = False
                                print("平仓 - 止损(1): ", self.get_current_price(0), self.broker.getvalue())
                        elif curr_price-open_price >= 200:
                            self.close(data=self.datas[0])
                            self.is_overbought = False
                            print("平仓 - 止损(2): ", self.get_current_price(0), self.broker.getvalue())

            # 做多仓位
            else:
                pass
        
        # 暂无仓位
        else:
            signal = self.sigle()
            if signal == SignalType.SELL:
                if before_avg_volume_14 > 0:
                    vol_ratio = current_volume / before_avg_volume_14
                    if vol_ratio >= 1.5:  # 当前成交量是过去14期平均成交量的3倍以上
                        return  # 跳过交易，避免在异常高成交量时入场
                self.sell(data=self.datas[0], size=0.1)
                self.trade_count += 1
                print("做空: ", self.trade_count, self.get_current_price(0), self.broker.getvalue())
                print("Volume: ", current_volume, "AvgVolume14: ", before_avg_volume_14, "Ratio: ", current_volume/before_avg_volume_14 if before_avg_volume_14 > 0 else "N/A")

                if self.is_overbought == False:
                    self.is_overbought = True
                    # print("超买开始: ", self.get_current_price(0), self.broker.getvalue())