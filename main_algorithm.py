"""
Main Stock Market Analysis Algorithm
Computes technical indicators from OHLC data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple

# Import indicator calculation modules
from indicator_calculations.volatility_calc import calculate_volatility
from indicator_calculations.stochastic_rsi_calc import calculate_stochastic_rsi
from indicator_calculations.bollinger_bands_calc import calculate_bollinger_bands
from indicator_calculations.vwap_calc import calculate_vwap
from indicator_calculations.ohlc_aggregator import aggregate_daily_to_weekly, validate_ohlc_data
from indicator_calculations.moving_averages_calc import calculate_10_ma, calculate_20_ma
from indicator_calculations.trading_signals_increasing_market import detect_increasing_market_signals


class StockAnalyzer:
    """
    Main class for stock market analysis using OHLC data and technical indicators
    """
    
    def __init__(self):
        self.indicators = {}
    
    def analyze_stock(self, ohlc_data: pd.DataFrame, stock_name: str) -> Dict:
        """
        Analyze a single stock using OHLC data and compute indicators
        
        Args:
            ohlc_data: DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            stock_name: Name of the stock
            
        Returns:
            Dictionary containing computed indicators (daily and weekly)
        """
        
        # Validate OHLC data
        if not validate_ohlc_data(ohlc_data):
            raise ValueError(f"Invalid OHLC data for {stock_name}")
        
        # Calculate all technical indicators (both daily and weekly)
        volatility_data = calculate_volatility(ohlc_data)
        stoch_rsi_data = calculate_stochastic_rsi(ohlc_data)
        bb_data = calculate_bollinger_bands(ohlc_data)
        vwap_data = calculate_vwap(ohlc_data)
        
        # Calculate moving averages
        ma10 = calculate_10_ma(ohlc_data)
        ma20 = calculate_20_ma(ohlc_data)
        
        # Store indicators
        self.indicators = {
            'daily_volatility': volatility_data['daily_volatility'],
            'weekly_volatility': volatility_data['weekly_volatility'],
            'daily_stochastic_rsi': stoch_rsi_data['daily_stochastic_rsi'],
            'weekly_stochastic_rsi': stoch_rsi_data['weekly_stochastic_rsi'],
            'daily_bollinger_bands': bb_data['daily_bollinger_bands'],
            'weekly_bollinger_bands': bb_data['weekly_bollinger_bands'],
            'daily_vwap': vwap_data['daily_vwap'],
            'weekly_vwap': vwap_data['weekly_vwap'],
            'ma_10': ma10,
            'ma_20': ma20
        }
        
        # Automatically detect trading signals for increasing market scenarios
        signals = self.detect_trading_signals(ohlc_data)
        
        return {
            'stock_name': stock_name,
            'indicators': self.indicators,
            'ohlc_data': ohlc_data,
            'trading_signals': signals
        }
    
    def analyze_multiple_stocks(self, stocks_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Analyze multiple stocks and return combined results
        
        Args:
            stocks_data: Dictionary with stock names as keys and OHLC DataFrames as values
            
        Returns:
            Dictionary containing analysis results for all stocks
        """
        all_results = {}
        
        for stock_name, ohlc_data in stocks_data.items():
            print(f"Analyzing {stock_name}...")
            result = self.analyze_stock(ohlc_data, stock_name)
            all_results[stock_name] = result
        
        return all_results
    
    def detect_trading_signals(self, ohlc_data: pd.DataFrame, lookback_days: int = None) -> List[Dict]:
        """
        Detect trading signals for increasing market scenarios
        
        Args:
            ohlc_data: DataFrame with OHLC data
            lookback_days: Number of days to check for signals (None for all)
            
        Returns:
            List of dictionaries containing detected signals
        """
        if not hasattr(self, 'indicators') or not self.indicators:
            raise ValueError("Must call analyze_stock() first to calculate indicators")
        
        signals = []
        end_idx = len(ohlc_data)
        start_idx = max(20, end_idx - lookback_days) if lookback_days else 20
        
        for idx in range(start_idx, end_idx):
            signal = detect_increasing_market_signals(ohlc_data, self.indicators, idx)
            if signal:
                signal['date'] = ohlc_data.iloc[idx]['Date'] if 'Date' in ohlc_data.columns else ohlc_data.index[idx]
                signal['index'] = idx
                signals.append(signal)
        
        return signals
    
    # Note: Export functionality removed. Integrate your own persistence/export as needed.


def main():
    """
    Main function - ready for API data integration
    
    Example usage:
        analyzer = StockAnalyzer()
        result = analyzer.analyze_stock(ohlc_data, "AAPL")
        signals = result['trading_signals']
        
        for signal in signals:
            print(f"Case {signal['case']}: Entry={signal['entry_price']:.2f}, "
                  f"SL={signal['stop_loss']:.2f}, Target={signal['target']:.2f}")
    """
    print("Stock Market Analysis Algorithm")
    print("Ready for API data integration")
    print("\nFeatures:")
    print("- Calculates technical indicators (Volatility, Stochastic RSI, Bollinger Bands, VWAP, Moving Averages)")
    print("- Detects trading signals for increasing market scenarios (Cases 1.a, 1.b, 1.c)")
    print("- Automatically identifies falling/sideways market conditions during uptrends")
    print("\nUse StockAnalyzer class to analyze OHLC data")
    print("Example: analyzer = StockAnalyzer()")
    print("         result = analyzer.analyze_stock(ohlc_data, 'STOCK_NAME')")
    print("         signals = result['trading_signals']")


if __name__ == "__main__":
    main()
