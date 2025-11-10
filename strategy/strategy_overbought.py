import backtrader as bt
import backtrader.indicators as btind


class StrategyOverbought(bt.Strategy):
      """ 策略-超买
      """

      def __init__(self):
            # 多时间框架指标参数存储(key:data.index / val:ind.value)
            self.timeframe_indicators = {}
            for i in range(len(self.datas)):
                  btind.ExponentialMovingAverage(
                  self.datas[0], period=20)
                  btind.ExponentialMovingAverage(
                  self.datas[0], period=200)
                  btind.BollingerBands(
                  self.datas[0], period=200)