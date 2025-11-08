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
		exchange.BinanceProductionBaseURL, key, secret)

	// start := "2025-10-01 00:00:00"
	end := "2025-09-01 00:00:00"
	// startTime, _ := time.Parse(exchange.TimeLayout, start)
	endTime, _ := time.Parse(exchange.TimeLayout, end)
	limit := 1000
	for _, item := range []exchange.KlineInterval{
		exchange.KlineInterval_5m,
		exchange.KlineInterval_15m,
		exchange.KlineInterval_1h,
		exchange.KlineInterval_4h,
		// exchange.KlineInterval_1d,
		// exchange.KlineInterval_1w,
	} {
		klines, err := connector.Klines(
			item,
			// uint64(startTime.UnixMilli()),
			0,
			uint64(endTime.UnixMilli()),
			// 0,
			limit,
		)

		if err != nil {
			panic(err)
		}
		fmt.Printf("%s count:%d\n", item, len(klines))

		// klines -> data.json  local file
		// 将结构体切片转换为 JSON
		data, err := json.MarshalIndent(klines, "", "  ")
		if err != nil {
			panic(err)
		}

		// 写入文件
		fn := fmt.Sprintf("../data/%s_%s.json", "BTCUSDT", item)
		if err = os.WriteFile(fn, data, 0644); err != nil {
			panic(err)
		}
	}
}
