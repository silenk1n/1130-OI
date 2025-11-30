#!/usr/bin/env python3
"""
Utility script to get all available USDT perpetual trading pairs from Binance
"""

import requests
import json


def get_usdt_perpetual_symbols():
    """Get all USDT perpetual trading pairs"""
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        usdt_symbols = []
        for symbol_info in data["symbols"]:
            if (symbol_info["quoteAsset"] == "USDT" and
                symbol_info["contractType"] == "PERPETUAL" and
                symbol_info["status"] == "TRADING"):
                usdt_symbols.append(symbol_info["symbol"])

        return sorted(usdt_symbols)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange info: {e}")
        return []


def get_top_symbols_by_volume(limit: int = 20):
    """Get top USDT perpetual symbols by 24h trading volume"""
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Filter USDT perpetual symbols and sort by quote volume
        usdt_symbols = []
        for ticker in data:
            if ticker["symbol"].endswith("USDT"):
                usdt_symbols.append({
                    "symbol": ticker["symbol"],
                    "volume": float(ticker["quoteVolume"])
                })

        # Sort by volume descending
        usdt_symbols.sort(key=lambda x: x["volume"], reverse=True)

        return [symbol["symbol"] for symbol in usdt_symbols[:limit]]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching 24hr ticker data: {e}")
        return []


def main():
    print("Getting all USDT perpetual trading pairs...")

    # Get all symbols
    all_symbols = get_usdt_perpetual_symbols()
    print(f"Total USDT perpetual symbols: {len(all_symbols)}")
    print("\nFirst 20 symbols:")
    for symbol in all_symbols[:20]:
        print(f"  {symbol}")

    print("\n" + "="*50)

    # Get top symbols by volume
    print("\nTop 20 symbols by 24h trading volume:")
    top_symbols = get_top_symbols_by_volume(20)
    for i, symbol in enumerate(top_symbols, 1):
        print(f"  {i:2d}. {symbol}")


if __name__ == "__main__":
    main()