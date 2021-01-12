package hello

import (
	qq "rsc.io/quote"
	quoteV3 "rsc.io/quote/v3"
)

func Hello() string {
	return qq.Hello()
}

func Proverb() string {
	return quoteV3.Concurrency()
}
