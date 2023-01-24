package main

import (
	"fmt"
	"time"

	"github.com/cmarkh/go-bbg"
)

func main() {
	t := time.Now()

	tickers := []string{"AAPL Equity"}
	fields := []string{"LONG_COMP_NAME", "SECURITY_TYP2", "EQY_SH_OUT_REAL"}
	//overrides := bbg.Override{Field: "EQY_FUND_CRNCY", Value: "EUR"}

	resp, _, _, err := bbg.Ref(tickers, fields)
	fmt.Println(resp)
	fmt.Println(err)

	fmt.Println(time.Since(t))
}
