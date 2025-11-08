import backtrader as bt
import backtrader.indicators as btind


import backtrader as bt
import backtrader.indicators as btind

class Strategy(bt.Strategy):
    params = (
        ('printlog', True),
    )
    
    def __init__(self):
        # 存储指标的字典
        self.indicators = {}
        
        for i in range(len(self.datas)):
            data_name = self.datas[i]._name if hasattr(self.datas[i], '_name') else f'data{i}'
            self.indicators[data_name] = {}
            
            # 创建技术指标
            self.indicators[data_name]['ema20'] = btind.ExponentialMovingAverage(
                self.datas[i], period=20)
            self.indicators[data_name]['ema200'] = btind.ExponentialMovingAverage(
                self.datas[i], period=200)
            self.indicators[data_name]['boll'] = btind.BollingerBands(
                self.datas[i], period=200)
        
        # 订单跟踪
        self.order = None
        
    def are_indicators_ready(self, data_name):
        """检查指标是否已计算完成（避免使用NaN值）"""
        ind = self.indicators[data_name]
        
        # 检查是否有足够的数据计算指标
        conditions = [
            len(ind['ema20']) >= 20,      # EMA20需要20根K线
            len(ind['ema200']) >= 200,    # EMA200需要200根K线
            len(ind['boll']) >= 200,      # 布林带需要200根K线
            not bt.math.isnan(ind['ema20'][0]),    # 当前值不是NaN
            not bt.math.isnan(ind['ema200'][0]),
            not bt.math.isnan(ind['boll'].top[0]),
            not bt.math.isnan(ind['boll'].bot[0]),
        ]
        
        return all(conditions)
    
    def is_short_signal(self, data_name):
        """检查做空信号条件"""
        if not self.are_indicators_ready(data_name):
            return False
            
        ind = self.indicators[data_name]
        current_data = self.get_data_by_name(data_name)
        current_price = current_data.close[0]
        
        # 做空条件：价格高于EMA20、EMA200和布林带上轨
        conditions = [
            current_price > ind['ema20'][0],           # 价格 > EMA20
            current_price > ind['ema200'][0],         # 价格 > EMA200
            current_price > ind['boll'].top[0],       # 价格 > 布林带上轨
        ]
        
        return all(conditions)

    def is_exit_signal(self, data_name):
        """检查平仓信号条件"""
        if not self.position or not self.are_indicators_ready(data_name):
            return False
            
        ind = self.indicators[data_name]
        current_data = self.get_data_by_name(data_name)
        current_price = current_data.close[0]
        
        # 平仓条件1：价格触及布林带下轨
        exit_condition_1 = current_price <= ind['boll'].bot[0]
        return exit_condition_1
    
    def get_data_by_name(self, data_name):
        """通过名称获取数据对象"""
        for data in self.datas:
            if hasattr(data, '_name') and data._name == data_name:
                return data
        return self.datas[0]  # 默认返回第一个数据
    
    def next(self):
        
        # 检查平仓信号（优先于开仓）
        if self.position and self.position.size < 0:  # 持有空单
            for data_name in self.indicators.keys():
                if self.is_exit_signal(data_name):
                    self.close_short_position(data_name)
                    return  # 平仓后不再开新仓
                

        # 如果有未完成订单，跳过
        if self.order:
            return
        
        # 检查每个时间框架的做空信号
        for data_name in self.indicators.keys():
            if self.is_short_signal(data_name):
                # 获取对应的数据源
                data = self.get_data_by_name(data_name)
                current_price = data.close[0]
                
                if not self.position:  # 没有持仓时开空单
                    self.open_short_position(data, current_price, data_name)
            
    def open_short_position(self, data, price, data_name):
        """开空单"""
        # 下空单（卖出开空）
        self.order = self.sell(data=data)
        
        if self.p.printlog:
            print(f'{data.datetime.datetime(0)} - {data_name} - 做空信号触发')
            print(f'  价格: {price:.2f}')
            print(f'  EMA20: {self.indicators[data_name]["ema20"][0]:.2f}')
            print(f'  EMA200: {self.indicators[data_name]["ema200"][0]:.2f}')
            print(f'  布林上轨: {self.indicators[data_name]["boll"].top[0]:.2f}')
    
    def close_and_short(self, data, price, data_name):
        """平多单并开空单"""
        if self.position.size > 0:  # 当前持有多单
            # 先平多单
            self.order = self.close(data=data)
            if self.p.printlog:
                print(f'{data.datetime.datetime(0)} - 平多单，准备做空')
        else:  # 当前持有空单，但信号仍然有效，可以加仓或持有
            if self.p.printlog:
                print(f'{data.datetime.datetime(0)} - 空单信号持续，持有空单')

    def close_short_position(self, data_name):
        """平空单"""
        data = self.get_data_by_name(data_name)
      #   current_price = data.close[0]
        
        # 平仓（买入平空）
        self.order = self.close(data=data)
        
       
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交/接受，无需处理
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                order_type = "买入"
            elif order.issell():
                order_type = "做空" if order.size < 0 else "平仓"
            
            if self.p.printlog:
                print(f'{order.data.datetime.datetime(0)} - {order_type}订单完成: '
                      f'价格={order.executed.price:.2f}, '
                      f'数量={order.executed.size}, '
                      f'成本={order.executed.comm:.2f}')
            
            self.order = None
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.p.printlog:
                print(f'订单取消/保证金不足/拒绝: {order.status}')
            self.order = None