package exchange

import (
	"fmt"
	"time"

	"github.com/shopspring/decimal"
)

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

type Kline struct {
	OpenTime                uint64 `json:"openTime"`
	Open                    string `json:"open"`
	High                    string `json:"high"`
	Low                     string `json:"low"`
	Close                   string `json:"close"`
	Volume                  string `json:"volume"`
	CloseTime               uint64 `json:"closeTime"`
	QuoteAssetVolume        string `json:"quoteAssetVolume"`
	NumberOfTrades          uint64 `json:"numberOfTrades"`
	TakerBuyBaseAssetVolume string `json:"takerBuyBaseAssetVolume"`
	// TakerBuyQuoteAssetVolume  string `json:"takerBuyQuoteAssetVolume"`
	TakerSellBaseAssetVolume string `json:"takerSellBaseAssetVolume"`
	// TakerSellQuoteAssetVolume string `json:"takerSellQuoteAssetVolume"`
	BuyRatio  string `json:"buyRatio"`
	SellRatio string `json:"sellRatio"`
}

func (kline *Kline) String() string {
	openTime := time.UnixMilli(int64(kline.OpenTime)).Format(TimeLayout)
	totalVolume, _ := decimal.NewFromString(kline.Volume)
	buyVolume, _ := decimal.NewFromString(kline.TakerBuyBaseAssetVolume)
	sellVolume := totalVolume.Sub(buyVolume)
	buyRatio := buyVolume.Div(totalVolume).Mul(decimal.NewFromInt(100)).StringFixed(2) + "%"
	sellRatio := sellVolume.Div(totalVolume).Mul(decimal.NewFromInt(100)).StringFixed(2) + "%"
	return fmt.Sprintf(`
	[%s]:
	O: %s H: %s L: %s C: %s
	Volume: %s | Buy: %s(%s)/Sell: %s(%s)
	`,
		openTime,
		kline.Open,
		kline.High,
		kline.Low,
		kline.Close,
		totalVolume.String(),
		buyVolume.String(),
		buyRatio,
		sellVolume.String(),
		sellRatio,
	)
}
