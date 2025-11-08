package exchange

import (
	"context"
	"encoding/json"
	"sync"

	sdk "github.com/binance/binance-connector-go"
	"github.com/shopspring/decimal"
)

var (
	instance *BinanceConnector
	once     sync.Once
)

type BinanceConnector struct {
	client *sdk.Client

	symbol            string
	symbolTickerPrice decimal.Decimal
	totalBalance      decimal.Decimal
}

func GetBinanceConnector(baseURL, key, secret string) *BinanceConnector {
	once.Do(func() {
		instance = &BinanceConnector{
			client: sdk.NewClient(key, secret, baseURL),

			symbol:            "BTCUSDT",
			symbolTickerPrice: decimal.Zero,
		}
		if err := instance.onUpdateSymbolTickerPrice(); err != nil {
			panic(err)
		}

		/*
			go func() {
				for {
					<-time.After(time.Second)
					if err := instance.onUpdateSymbolTickerPrice(); err != nil {
						log.Printf("[ERROR]UpdateSymbolTickerPrice: %v\n", err)
						continue
					}
				}
			}()
		*/
	})
	return instance
}

func (bc *BinanceConnector) onUpdateSymbolTickerPrice() error {
	resp, err := bc.client.NewTickerPriceService().Symbol(bc.symbol).Do(context.Background())
	if err != nil {
		return err
	}
	for _, item := range resp {
		if item.Symbol == bc.symbol {
			price, err := decimal.NewFromString(item.Price)
			if err != nil {
				return err
			}
			bc.symbolTickerPrice = price
			return nil
		}
	}
	return nil
}

func (bc *BinanceConnector) Balance() decimal.Decimal {
	resp, err := bc.client.NewWalletBalanceService().Do(context.Background())
	if err != nil {
		return decimal.Zero
	}
	for _, item := range resp {
		if item.WalletName == "USDⓈ-M Futures" {
			balanceBTC, err := decimal.NewFromString(item.Balance)
			if err != nil {
				return decimal.Zero
			}
			bc.totalBalance = balanceBTC.Mul(bc.symbolTickerPrice)
			break
		}
	}
	return bc.totalBalance
}

func (bc *BinanceConnector) Klines(interval KlineInterval, startTime, endTime uint64, limit int) ([]Kline, error) {
	klineService := bc.client.NewKlinesService()
	klineService.Symbol(bc.symbol)
	klineService.Interval(string(interval))
	if startTime > 0 {
		klineService.StartTime(startTime)
	}
	klineService.EndTime(endTime)
	if limit > 0 {
		klineService.Limit(limit)
	}
	resp, err := klineService.Do(context.Background())
	if err != nil {
		return nil, err
	}
	var klines []Kline
	for _, item := range resp {
		buf, _ := json.Marshal(item)
		var kline Kline
		if err := json.Unmarshal(buf, &kline); err != nil {
			return nil, err
		}
		kline.Complete()
		klines = append(klines, kline)
	}
	return klines, nil
}
