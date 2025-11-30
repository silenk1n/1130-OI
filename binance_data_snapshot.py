#!/usr/bin/env python3
"""
Binance Perpetual Futures USDT Trading Pair Data Snapshot

This script fetches key metrics for Binance perpetual futures USDT trading pairs:
- mark_price (标记价格)
- index_price (指数价格)
- basis (基差)
- basis_percent (基差百分比)
- last_funding_rate (最新资金费率)
- oi (持仓量)
- long_short_account_ratio (账户多空比)
- top_trader_account_ls_ratio (大户账户多空比)
- top_trader_position_ls_ratio (大户持仓多空比)
- taker_buy_sell_ratio (主动买卖比)
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class BinanceDataSnapshot:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.futures_data_url = "https://fapi.binance.com/futures/data"

    def get_mark_price(self, symbol: str) -> Dict[str, Any]:
        """Get mark price and funding rate for a symbol"""
        url = f"{self.base_url}/fapi/v1/premiumIndex"
        params = {"symbol": symbol}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching mark price for {symbol}: {e}")
            return {}

    def get_index_price(self, symbol: str) -> Optional[float]:
        """Get index price for a symbol"""
        # For USDT perpetual contracts, the index price is often available in the premiumIndex endpoint
        mark_data = self.get_mark_price(symbol)
        if mark_data and "indexPrice" in mark_data:
            return float(mark_data["indexPrice"])

        # Fallback to indexInfo endpoint
        url = f"{self.base_url}/fapi/v1/indexInfo"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Find the symbol in the composite index data
            for item in data:
                if item.get("symbol") == symbol:
                    return float(item.get("indexPrice", 0))
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching index price for {symbol}: {e}")
            return None

    def calculate_basis(self, mark_price: float, index_price: float) -> Dict[str, float]:
        """Calculate basis and basis percentage"""
        if index_price == 0:
            return {"basis": 0, "basis_percent": 0}

        basis = mark_price - index_price
        basis_percent = (basis / index_price) * 100

        return {
            "basis": basis,
            "basis_percent": basis_percent
        }

    def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        """Get latest funding rate for a symbol"""
        url = f"{self.base_url}/fapi/v1/fundingRate"
        params = {"symbol": symbol, "limit": 1}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching funding rate for {symbol}: {e}")
            return {}

    def get_open_interest(self, symbol: str) -> Dict[str, Any]:
        """Get open interest for a symbol"""
        url = f"{self.base_url}/fapi/v1/openInterest"
        params = {"symbol": symbol}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching open interest for {symbol}: {e}")
            return {}

    def get_long_short_ratio(self, symbol: str, period: str = "5m", limit: int = 1) -> Dict[str, Any]:
        """Get long/short ratio data for different categories"""

        def fetch_ratio(endpoint: str) -> List[Dict]:
            url = f"{self.futures_data_url}/{endpoint}"
            params = {
                "symbol": symbol,
                "period": period,
                "limit": limit
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {endpoint} for {symbol}: {e}")
                return []

        # Fetch all ratio types
        account_ratio = fetch_ratio("globalLongShortAccountRatio")
        top_account_ratio = fetch_ratio("topLongShortAccountRatio")
        top_position_ratio = fetch_ratio("topLongShortPositionRatio")

        return {
            "long_short_account_ratio": account_ratio[0] if account_ratio else {},
            "top_trader_account_ls_ratio": top_account_ratio[0] if top_account_ratio else {},
            "top_trader_position_ls_ratio": top_position_ratio[0] if top_position_ratio else {}
        }

    def get_taker_buy_sell_ratio(self, symbol: str, period: str = "5m", limit: int = 1) -> Dict[str, Any]:
        """Get taker buy/sell volume ratio"""
        url = f"{self.futures_data_url}/takerlongshortRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "limit": limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching taker buy/sell ratio for {symbol}: {e}")
            return {}

    def get_data_snapshot(self, symbol: str) -> Dict[str, Any]:
        """Get complete data snapshot for a symbol"""
        print(f"Fetching data snapshot for {symbol}...")

        # Get mark price and funding rate
        mark_data = self.get_mark_price(symbol)
        mark_price = float(mark_data.get("markPrice", 0)) if mark_data else 0

        # Get index price
        index_price = self.get_index_price(symbol) or 0

        # Calculate basis
        basis_data = self.calculate_basis(mark_price, index_price)

        # Get funding rate
        funding_data = self.get_funding_rate(symbol)

        # Get open interest
        oi_data = self.get_open_interest(symbol)

        # Get long/short ratios
        ratio_data = self.get_long_short_ratio(symbol)

        # Get taker buy/sell ratio
        taker_data = self.get_taker_buy_sell_ratio(symbol)

        # Compile complete snapshot
        snapshot = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "mark_price": mark_price,
            "index_price": index_price,
            "basis": basis_data["basis"],
            "basis_percent": basis_data["basis_percent"],
            "last_funding_rate": float(funding_data.get("fundingRate", 0)) if funding_data else 0,
            "next_funding_time": funding_data.get("fundingTime", 0) if funding_data else 0,
            "oi": float(oi_data.get("openInterest", 0)) if oi_data else 0,
            "long_short_account_ratio": float(ratio_data.get("long_short_account_ratio", {}).get("longShortRatio", 0)) if ratio_data.get("long_short_account_ratio") else 0,
            "top_trader_account_ls_ratio": float(ratio_data.get("top_trader_account_ls_ratio", {}).get("longShortRatio", 0)) if ratio_data.get("top_trader_account_ls_ratio") else 0,
            "top_trader_position_ls_ratio": float(ratio_data.get("top_trader_position_ls_ratio", {}).get("longShortRatio", 0)) if ratio_data.get("top_trader_position_ls_ratio") else 0,
            "taker_buy_sell_ratio": float(taker_data.get("buySellRatio", 0)) if taker_data else 0
        }

        return snapshot

    def get_multiple_symbols_snapshot(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get data snapshot for multiple symbols"""
        snapshots = {}

        for symbol in symbols:
            snapshot = self.get_data_snapshot(symbol)
            snapshots[symbol] = snapshot

            # Add small delay to avoid rate limiting
            time.sleep(0.1)

        return snapshots


def main():
    """Example usage"""
    snapshot = BinanceDataSnapshot()

    # Example symbols (you can add more)
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]

    print("Fetching Binance Perpetual Futures Data Snapshot...")
    print("=" * 80)

    data = snapshot.get_multiple_symbols_snapshot(symbols)

    for symbol, snapshot_data in data.items():
        print(f"\n{symbol}:")
        print(f"  标记价格 (Mark Price): {snapshot_data['mark_price']:.2f}")
        print(f"  指数价格 (Index Price): {snapshot_data['index_price']:.2f}")
        print(f"  基差 (Basis): {snapshot_data['basis']:.4f}")
        print(f"  基差百分比 (Basis %): {snapshot_data['basis_percent']:.4f}%")
        print(f"  最新资金费率 (Funding Rate): {snapshot_data['last_funding_rate']:.6f}")
        print(f"  持仓量 (OI): {snapshot_data['oi']:.2f}")
        print(f"  账户多空比 (LS Account Ratio): {snapshot_data['long_short_account_ratio']:.4f}")
        print(f"  大户账户多空比 (Top Trader LS Account): {snapshot_data['top_trader_account_ls_ratio']:.4f}")
        print(f"  大户持仓多空比 (Top Trader LS Position): {snapshot_data['top_trader_position_ls_ratio']:.4f}")
        print(f"  主动买卖比 (Taker Buy/Sell): {snapshot_data['taker_buy_sell_ratio']:.4f}")
        print(f"  时间戳: {snapshot_data['timestamp']}")


if __name__ == "__main__":
    main()