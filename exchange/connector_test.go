package exchange_test

import (
	"encoding/json"
	"fmt"
	"os"
	"testing"
	"time"
	"trading_helper/exchange"
)

const (
	key    = "6xUgCXmQ9zCnxXygzCIuFEC9PysFqDENOdE82tF0RHsISDZ9KtCD5r4kkTvhSBPs"
	secret = "cWPLmSasjcATAs9fFnn69z2xRlju67wPpVTr7ddO6s2UvWSe32Z2sIPheYyUog1T"
)

func TestMain(t *testing.T) {
	connector := exchange.GetBinanceConnector(exchange.BinanceProductionBaseURL, key, secret)

	// 更合理的时间范围（使用过去的数据，避免未来日期）
	now := time.Now()
	startTime := now.AddDate(0, -2, 0) // 3个月前
	endTime := now.AddDate(0, 0, 0)    // 1个月前

	limit := 1000

	intervals := []exchange.KlineInterval{
		exchange.KlineInterval_5m,
		exchange.KlineInterval_15m,
		exchange.KlineInterval_1h,
		exchange.KlineInterval_4h,
		exchange.KlineInterval_1d,
	}

	for _, item := range intervals {
		startAt := startTime.UnixMilli()
		endAt := endTime.UnixMilli()

		// 获取时间间隔（毫秒）
		intervalMs := getIntervalMilliseconds(item)
		if intervalMs == 0 {
			fmt.Printf("不支持的K线间隔: %s\n", item)
			continue
		}

		fmt.Printf("正在获取 %s K线数据...\n", item)

		var totalKlines []exchange.Kline
		currentStart := startAt

		for currentStart < endAt {
			// 计算本次请求的结束时间
			requestEnd := currentStart + int64(limit)*intervalMs
			if requestEnd > endAt {
				requestEnd = endAt
			}

			klines, err := connector.Klines(item,
				uint64(currentStart),
				uint64(requestEnd),
				limit)
			if err != nil {
				panic(fmt.Sprintf("获取K线数据失败: %v", err))
			}

			if len(klines) == 0 {
				break // 没有更多数据
			}

			totalKlines = append(totalKlines, klines...)

			// 更新下一次请求的起始时间（使用最后一根K线的结束时间）
			lastKlineTime := int64(klines[len(klines)-1].OpenTime)
			currentStart = lastKlineTime + intervalMs

			// 添加延迟避免API限制
			time.Sleep(100 * time.Millisecond)
		}

		// 去重处理
		totalKlines = removeDuplicateKlines(totalKlines)

		fmt.Printf("✅ %s 完成: 共 %d 根K线\n", item, len(totalKlines))

		// 保存数据
		if err := saveKlinesToFile(totalKlines, "BTCUSDT", item); err != nil {
			panic(fmt.Sprintf("保存数据失败: %v", err))
		}
	}
}

// 获取K线间隔的毫秒数
func getIntervalMilliseconds(interval exchange.KlineInterval) int64 {
	switch interval {
	case exchange.KlineInterval_5m:
		return 5 * 60 * 1000
	case exchange.KlineInterval_15m:
		return 15 * 60 * 1000
	case exchange.KlineInterval_1h:
		return 60 * 60 * 1000
	case exchange.KlineInterval_4h:
		return 4 * 60 * 60 * 1000
	case exchange.KlineInterval_1d:
		return 24 * 60 * 60 * 1000
	case exchange.KlineInterval_1w:
		return 7 * 24 * 60 * 1000
	default:
		return 0
	}
}

// 去除重复的K线
func removeDuplicateKlines(klines []exchange.Kline) []exchange.Kline {
	seen := make(map[uint64]bool)
	result := []exchange.Kline{}

	for _, kline := range klines {
		if !seen[kline.OpenTime] {
			seen[kline.OpenTime] = true
			result = append(result, kline)
		}
	}
	return result
}

// 保存K线数据到文件
func saveKlinesToFile(klines []exchange.Kline, symbol string, interval exchange.KlineInterval) error {
	data, err := json.MarshalIndent(klines, "", "  ")
	if err != nil {
		return err
	}

	filename := fmt.Sprintf("../data/%s_%s.json", symbol, interval)
	return os.WriteFile(filename, data, 0644)
}
