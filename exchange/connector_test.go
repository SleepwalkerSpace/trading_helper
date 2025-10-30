package exchange_test

import (
	"testing"
	"trading_helper/exchange"
)

func TestGetBinanceConnector(t *testing.T) {
	tests := []struct {
		name string // description of this test case
		// Named input parameters for target function.
		endpoint  string
		apiKey    string
		secretKey string
		want      *exchange.BinanceConnector
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := exchange.GetBinanceConnector(tt.endpoint, tt.apiKey, tt.secretKey)
			// TODO: update the condition below to compare got with tt.want.
			if true {
				t.Errorf("GetBinanceConnector() = %v, want %v", got, tt.want)
			}
		})
	}
}
