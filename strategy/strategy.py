import backtrader as bt
import backtrader.indicators as btind

class Strategy(bt.Strategy):
    params = (
        ('printlog', True),
        ('add_position_threshold', 1250),
        ('max_add_times', 4),             # 最大补仓次数
    )
    
    def __init__(self):
        self.leverage = 100
        # 存储指标的字典
        self.indicators = {}

        self.history_rsi_vals = []
        
        for i in range(len(self.datas)):
            data_name = self.datas[i]._name if hasattr(self.datas[i], '_name') else f'data{i}'
            self.indicators[data_name] = {}
            
            # 创建技术指标
            self.indicators[data_name]['volume_sma'] = btind.SMA(self.datas[i].volume, period=200)
            self.indicators[data_name]['ema20'] = btind.ExponentialMovingAverage(
                self.datas[i], period=20)
            self.indicators[data_name]['ema200'] = btind.ExponentialMovingAverage(
                self.datas[i], period=200)
            self.indicators[data_name]['boll'] = btind.BollingerBands(
                self.datas[i], period=200)
            self.indicators[data_name]['rsi_ema'] = btind.RSI_EMA(self.datas[i], period=14, upperband=70, lowerband=30, plot=True)
          
        # 订单跟踪和持仓管理
        self.order = None
        self.entry_price = 0           # 开仓价格
        self.entry_time = None         # 开仓时间
        self.position_size = 0         # 持仓数量
        self.add_position_count = 0    # 补仓次数
        self.last_add_price = 0        # 上次补仓价格

        self.exit_condition_1 = False
        
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
            ind['ema20'][0] >= ind['boll'].top[0],
        ]
        ok = all(conditions)
        # if ok:
        #    print("rsi_ema? ",ind['rsi_ema'][0])
        return all(conditions)

    def is_exit_signal(self, data_name):
        """检查平仓信号条件"""
        if not self.position or not self.are_indicators_ready(data_name):
            return False
            
        ind = self.indicators[data_name]
        current_data = self.get_data_by_name(data_name)
        current_price = current_data.close[0]
        
        # 平仓条件1：价格触及布林带下轨
        current_exit_condition_1 = current_price <= ind['boll'].bot[0]
        if self.exit_condition_1 == False:
            self.exit_condition_1 = current_exit_condition_1

        # self.history_rsi_vals 最新的3个值不是递减
        last_rsi_ema_vals_3 = self.history_rsi_vals[-3:]

        c1 = (self.exit_condition_1 and last_rsi_ema_vals_3[1] < last_rsi_ema_vals_3[2])
        c2 = self.exit_condition_1 and current_exit_condition_1 == False
        return  c1 or c2
    
    def should_add_position(self, data_name):
        """检查是否需要补仓"""
        if not self.position or self.position.size >= 0:
            return False  # 没有持仓或持有多单，不补仓
            
        if self.add_position_count >= self.p.max_add_times:
            return False  # 达到最大补仓次数
            
        current_data = self.get_data_by_name(data_name)
        current_price = current_data.close[0]
        
        price_above_entry = current_price >= self.entry_price + self.p.add_position_threshold
        price_above_last_add = current_price >= self.last_add_price + self.p.add_position_threshold
        
        if self.add_position_count == 0:
            return price_above_entry
        else:
            return price_above_last_add
    
    def get_data_by_name(self, data_name):
        """通过名称获取数据对象"""
        for data in self.datas:
            if hasattr(data, '_name') and data._name == data_name:
                return data
        return self.datas[0]  # 默认返回第一个数据
    
    def next(self):
        for data_name in self.indicators.keys():
            ind = self.indicators[data_name]

            self.history_rsi_vals.append(ind['rsi_ema'][0])

        if self.order:
            return
        
        # 检查平仓信号（优先于开仓和补仓）
        if self.position and self.position.size < 0:  # 持有空单
            for data_name in self.indicators.keys():
                if self.is_exit_signal(data_name):
                    self.close_short_position(data_name)
                    return  # 平仓后不再开新仓或补仓
        
        # 检查补仓信号
        if self.position and self.position.size < 0:  # 持有空单
            for data_name in self.indicators.keys():
                if self.should_add_position(data_name):
                    self.add_short_position(data_name)
                    return  # 补仓后不再检查开仓
        
        # 检查开仓信号
        for data_name in self.indicators.keys():
            if self.is_short_signal(data_name):
                data = self.get_data_by_name(data_name)
                current_price = data.close[0]
                
                if not self.position:  # 没有持仓时开空单
                    self.open_short_position(data, current_price, data_name)
                    return  # 开仓后不再检查其他信号
    
    def open_short_position(self, data, price, data_name):
        """开空单"""
        # 计算初始仓位大小
        size = self.calculate_position_size(price)
        
        # 下空单（卖出开空）
        self.order = self.sell(data=data, size=size)
        
        # 记录开仓信息
        self.entry_price = price
        self.entry_time = data.datetime.datetime(0)
        self.position_size = size
        self.add_position_count = 0
        self.last_add_price = price  # 记录开仓价格作为补仓基准
        
        if self.p.printlog:
            print(f'\n🎯 开空单 - {data_name}')
            print(f'  时间: {self.entry_time}')
            print(f'  开仓价格: {price:.2f}')
            print(f'  开仓数量: {size}')
            print(f'  EMA20: {self.indicators[data_name]["ema20"][0]:.2f}')
            print(f'  EMA200: {self.indicators[data_name]["ema200"][0]:.2f}')
            print(f'  BOLL_TOP: {self.indicators[data_name]["boll"].top[0]:.2f}')
            print(f'  RSI_EMA: {self.indicators[data_name]["rsi_ema"][0]:.2f}')
    
    def add_short_position(self, data_name):
        """补仓空单"""
        data = self.get_data_by_name(data_name)
        current_price = data.close[0]
        
        # 计算补仓数量（可以按比例减少，避免风险过大）
        add_size = self.calculate_position_size(current_price)
        
        # 下补仓空单
        self.order = self.sell(data=data, size=add_size)
        
        # 更新持仓信息
        self.add_position_count += 1
        self.last_add_price = current_price
        self.position_size += add_size
        
        # 计算平均开仓价格
        total_value = (self.entry_price * (self.position_size - add_size) + 
                      current_price * add_size)
        self.entry_price = total_value / self.position_size  # 更新平均成本
        
        if self.p.printlog:
            print(f'\n📈 第{self.add_position_count}次补仓 - {data_name}')
            print(f'  时间: {data.datetime.datetime(0)}')
            print(f'  补仓价格: {current_price:.2f}')
            print(f'  补仓数量: {add_size}')
            print(f'  平均成本: {self.entry_price:.2f}')
            print(f'  总持仓: {self.position_size}')
            print(f'  当前浮动盈亏: {self.get_floating_pnl(current_price):+.2f}%')
    
    def close_short_position(self, data_name):
        """平空单"""
        data = self.get_data_by_name(data_name)
        current_price = data.close[0]
        
        # 平仓（买入平空）
        self.order = self.close(data=data)
        
        if self.p.printlog:
            pnl_percent = self.get_floating_pnl(current_price)
            print(f'\n💰 平仓 - {data_name}')
            print(f'  时间: {data.datetime.datetime(0)}')
            print(f'  平仓价格: {current_price:.2f}')
            print(f'  平均开仓价: {self.entry_price:.2f}')
            print(f'  持仓数量: {self.position_size}')
            print(f'  补仓次数: {self.add_position_count}')
            print(f'  最终盈亏: {pnl_percent:+.2f}%')
            
            if pnl_percent > 0:
                print('  ✅ 交易盈利')
            else:
                print('  ❌ 交易亏损')
        
        # 重置持仓信息
        self.reset_position_info()
    
    def calculate_position_size(self, price):
        """计算仓位大小"""
        fixed_amount = 50
        size = (fixed_amount * self.leverage) / price
        # .2f表示保留两位小数
        return round(size, 4)

    
    def get_floating_pnl(self, current_price):
        """计算浮动盈亏百分比"""
        if self.entry_price > 0:
            return (self.entry_price - current_price) / self.entry_price * 100 * self.leverage
        return 0
    
    def reset_position_info(self):
        """重置持仓信息"""
        self.entry_price = 0
        self.entry_time = None
        self.position_size = 0
        self.add_position_count = 0
        self.last_add_price = 0
        self.exit_condition_1 = False
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                order_type = "买入平仓"
            elif order.issell():
                if self.position and self.position.size < 0:
                    order_type = "补仓" if self.add_position_count > 0 else "开空"
                else:
                    order_type = "做空"
            
            if self.p.printlog:
                print(f'{order.data.datetime.datetime(0)} - {order_type}订单完成: '
                      f'价格={order.executed.price:.2f}, '
                      f'数量={order.executed.size}, '
                      f'余额={self.broker.getvalue():.2f}')
            
            self.order = None
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.p.printlog:
                print(f'订单取消/保证金不足/拒绝: {order.status}')
            self.order = None