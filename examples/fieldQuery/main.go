package main

import (
	"fmt"
	"log"

	"github.com/cmarkh/go-bbg"
)

func main() {
	bbIDs := []string{"AAPL Equity", "MSFT Equity"}

	fields := []string{"SECURITY_TYP"}
	//overrides := bbg.Override{Field: "EQY_FUND_CRNCY", Value: "EUR"}

	resp, _, _, err := bbg.Ref(bbIDs, fields)
	if err != nil {
		log.Fatal(err)
	}

	types := make(map[string]struct{})
	for _, r := range resp {
		v := fmt.Sprint(r.Value)
		if _, ok := types[v]; !ok {
			types[v] = struct{}{}
		}
	}

	for t := range types {
		fmt.Println(t)
	}

}
