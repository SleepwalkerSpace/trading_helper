from enum import Enum

class IndicatorType(Enum):
    """指标类型枚举"""
    VOLUME = "VOLUME"
    EMA_20 = "EMA_20"
    EMA_200 = "EMA_200"
    BOLL_200 = "BOLL_200"
    RSI_EMA = "RSI_EMA"

class SignalType(Enum):
    """交易类型枚举"""
    BUY = "BUY" # 做多
    SELL = "SELL" # 做空