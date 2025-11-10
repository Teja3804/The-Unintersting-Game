"""
Kite Connect Data Fetcher
Fetches OHLC data and integrates with StockAnalyzer
"""

from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Optional
from .kite_connector import KiteConnector
from main_algorithm import StockAnalyzer


class KiteDataFetcher:
    """
    Fetches market data from Kite Connect and analyzes using StockAnalyzer
    """
    
    def __init__(self, kite_connector: KiteConnector):
        """
        Initialize with authenticated KiteConnector
        
        Args:
            kite_connector: Authenticated KiteConnector instance
        """
        self.kite = kite_connector
        self.analyzer = StockAnalyzer()
    
    def fetch_and_analyze(self, exchange: str, symbol: str, days: int = 100,
                         interval: str = "day") -> Dict:
        """
        Fetch OHLC data and analyze for trading signals
        
        Args:
            exchange: Exchange name (e.g., "NSE", "BSE")
            symbol: Trading symbol (e.g., "RELIANCE", "TCS")
            days: Number of days of historical data to fetch
            interval: Data interval - "day", "minute", etc.
            
        Returns:
            Dictionary with analysis results and trading signals
        """
        # Get instrument token
        instrument_token = self.kite.get_instrument_token(exchange, symbol)
        if not instrument_token:
            raise ValueError(f"Instrument not found: {exchange}:{symbol}")
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        # Fetch OHLC data
        print(f"Fetching {days} days of data for {exchange}:{symbol}...")
        ohlc_data = self.kite.get_ohlc_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
        
        if ohlc_data.empty:
            raise ValueError(f"No data found for {exchange}:{symbol}")
        
        print(f"✓ Fetched {len(ohlc_data)} data points")
        
        # Analyze using StockAnalyzer
        print(f"Analyzing {symbol}...")
        result = self.analyzer.analyze_stock(ohlc_data, symbol)
        
        return {
            'symbol': symbol,
            'exchange': exchange,
            'instrument_token': instrument_token,
            'ohlc_data': ohlc_data,
            'analysis': result,
            'signals': result.get('trading_signals', [])
        }
    
    def fetch_multiple_symbols(self, symbols: list, exchange: str = "NSE", 
                              days: int = 100) -> Dict[str, Dict]:
        """
        Fetch and analyze multiple symbols
        
        Args:
            symbols: List of trading symbols
            exchange: Exchange name
            days: Number of days of historical data
            
        Returns:
            Dictionary with results for each symbol
        """
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.fetch_and_analyze(exchange, symbol, days)
            except Exception as e:
                print(f"✗ Error processing {symbol}: {str(e)}")
                results[symbol] = {'error': str(e)}
        
        return results

