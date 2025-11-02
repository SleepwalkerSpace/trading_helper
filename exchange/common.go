package exchange

const (
	BinanceProductionBaseURL string = "https://api.binance.com"
	BinanceTestnetBaseURL    string = "https://testnet.binance.vision"
)

const TimeLayout string = "2006-01-02 15:04:05"

type KlineInterval string

const (
	KlineInterval_5m  KlineInterval = "5m"
	KlineInterval_15m KlineInterval = "15m"
	KlineInterval_1h  KlineInterval = "1h"
	KlineInterval_4h  KlineInterval = "4h"
	KlineInterval_1d  KlineInterval = "1d"
	KlineInterval_1w  KlineInterval = "1w"
)
