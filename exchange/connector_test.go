package exchange_test

import (
	"fmt"
	"testing"
	"time"
	"trading_helper/exchange"
)

func TestMain(t *testing.T) {
	key := "6xUgCXmQ9zCnxXygzCIuFEC9PysFqDENOdE82tF0RHsISDZ9KtCD5r4kkTvhSBPs"
	secret := "cWPLmSasjcATAs9fFnn69z2xRlju67wPpVTr7ddO6s2UvWSe32Z2sIPheYyUog1T"
	connector := exchange.GetBinanceConnector(
		exchange.BinanceProductionBaseURL, key, secret)

	start := "2025-10-01 00:00:00"
	end := "2025-10-01 23:00:00"
	startTime, _ := time.ParseInLocation(exchange.TimeLayout, start, time.Local)
	endTime, _ := time.ParseInLocation(exchange.TimeLayout, end, time.Local)
	klines, err := connector.Klines(
		exchange.KlineInterval_1h,
		uint64(startTime.UnixMilli()),
		uint64(endTime.UnixMilli()),
	)
	if err != nil {
		panic(err)
	}
	fmt.Println("Klines count:", len(klines))
	for _, kline := range klines {
		fmt.Printf("%s\n", kline.String())
	}
}
