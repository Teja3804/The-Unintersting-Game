"""
Moving Averages Calculation Module
Calculates Simple Moving Averages (SMA) for stock analysis
"""

import pandas as pd
import numpy as np
from typing import Dict


def calculate_sma(prices: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: Series of closing prices
        window: Moving average window size
        
    Returns:
        Series of SMA values
    """
    return prices.rolling(window=window).mean()


def calculate_moving_averages(ohlc_data: pd.DataFrame, windows: list = [10, 20]) -> Dict[str, pd.Series]:
    """
    Calculate multiple moving averages
    
    Args:
        ohlc_data: DataFrame with OHLC data
        windows: List of window sizes for moving averages
        
    Returns:
        Dictionary with moving averages (key: 'ma_{window}')
    """
    prices = ohlc_data['Close']
    ma_dict = {}
    
    for window in windows:
        ma_dict[f'ma_{window}'] = calculate_sma(prices, window)
    
    return ma_dict


def calculate_10_ma(ohlc_data: pd.DataFrame) -> pd.Series:
    """
    Calculate 10-period Simple Moving Average
    
    Args:
        ohlc_data: DataFrame with OHLC data
        
    Returns:
        Series of 10 MA values
    """
    prices = ohlc_data['Close']
    return calculate_sma(prices, 10)


def calculate_20_ma(ohlc_data: pd.DataFrame) -> pd.Series:
    """
    Calculate 20-period Simple Moving Average
    
    Args:
        ohlc_data: DataFrame with OHLC data
        
    Returns:
        Series of 20 MA values
    """
    prices = ohlc_data['Close']
    return calculate_sma(prices, 20)


def are_mas_close(ma10: pd.Series, ma20: pd.Series, threshold_pct: float = 0.02) -> pd.Series:
    """
    Check if 10 MA and 20 MA are close to each other (within threshold percentage)
    
    Args:
        ma10: 10-period moving average
        ma20: 20-period moving average
        threshold_pct: Percentage threshold (default 2%)
        
    Returns:
        Boolean series indicating when MAs are close
    """
    diff_pct = abs(ma10 - ma20) / ma20
    return diff_pct <= threshold_pct

