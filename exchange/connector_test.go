package exchange_test

import (
	"encoding/json"
	"fmt"
	"os"
	"testing"
	"time"
	"trading_helper/exchange"
)

func TestMain(t *testing.T) {
	key := "6xUgCXmQ9zCnxXygzCIuFEC9PysFqDENOdE82tF0RHsISDZ9KtCD5r4kkTvhSBPs"
	secret := "cWPLmSasjcATAs9fFnn69z2xRlju67wPpVTr7ddO6s2UvWSe32Z2sIPheYyUog1T"
	connector := exchange.GetBinanceConnector(
		exchange.BinanceTestnetBaseURL, key, secret)

	start := "2025-11-01 00:00:00"
	end := "2025-11-07 23:00:00"
	startTime, _ := time.Parse(exchange.TimeLayout, start)
	endTime, _ := time.Parse(exchange.TimeLayout, end)
	klines, err := connector.Klines(
		exchange.KlineInterval_1h,
		uint64(startTime.UnixMilli()),
		uint64(endTime.UnixMilli()),
	)
	if err != nil {
		panic(err)
	}
	fmt.Println("Klines count:", len(klines))

	// klines -> data.json  local file
	// 将结构体切片转换为 JSON
	data, err := json.MarshalIndent(klines, "", "  ")
	if err != nil {
		panic(err)
	}

	// 写入文件
	fn := fmt.Sprintf("../data/%s_%s.json", "BTCUSDT", exchange.KlineInterval_1h)
	if err = os.WriteFile(fn, data, 0644); err != nil {
		panic(err)
	}
}
