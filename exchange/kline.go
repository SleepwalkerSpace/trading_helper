package exchange

import (
	"fmt"
	"time"

	"github.com/shopspring/decimal"
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

func (kline *Kline) Complete() {
	totalVolume, _ := decimal.NewFromString(kline.Volume)
	buyVolume, _ := decimal.NewFromString(kline.TakerBuyBaseAssetVolume)
	sellVolume := totalVolume.Sub(buyVolume)
	kline.TakerSellBaseAssetVolume = sellVolume.String()
	kline.BuyRatio = buyVolume.Div(totalVolume).Mul(decimal.NewFromInt(100)).StringFixed(2)
	kline.SellRatio = sellVolume.Div(totalVolume).Mul(decimal.NewFromInt(100)).StringFixed(2)
}

func (kline *Kline) String() string {
	openTime := time.UnixMilli(int64(kline.OpenTime)).Format(TimeLayout)
	totalVolume, _ := decimal.NewFromString(kline.Volume)
	buyVolume, _ := decimal.NewFromString(kline.TakerBuyBaseAssetVolume)
	sellVolume := totalVolume.Sub(buyVolume)
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
		kline.Volume,
		buyVolume.String(),
		kline.BuyRatio+"%",
		sellVolume.String(),
		kline.SellRatio+"%",
	)
}
