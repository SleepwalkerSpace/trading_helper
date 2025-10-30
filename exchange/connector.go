package exchange

import (
	"context"
	"sync"

	sdk "github.com/binance/binance-connector-go"
)

const (
	BinanceProductionEndpoint string = "https://api.binance.com"
	BinanceTestnetEndpoint    string = "https://testnet.binance.vision"
)

var (
	instance *BinanceConnector
	once     sync.Once
)

type BinanceConnector struct {
	client *sdk.Client
}

func GetBinanceConnector(endpoint, apiKey, secretKey string) *BinanceConnector {
	once.Do(func() {
		instance = &BinanceConnector{
			client: sdk.NewClient(apiKey, secretKey, endpoint),
		}
		instance.client.Debug = true
		ping := instance.client.NewPingService()
		err := ping.Do(context.Background())
		if err != nil {
			panic(err)
		}
	})
	return instance
}
