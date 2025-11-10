"""
Bollinger Bands Calculation Module
Calculates Bollinger Bands indicator for stock analysis
Supports both daily and weekly timeframes
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
from .ohlc_aggregator import aggregate_daily_to_weekly


def calculate_daily_bollinger_bands(daily_ohlc: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate daily Bollinger Bands
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Moving average window
        num_std: Number of standard deviations for bands
        
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    prices = daily_ohlc['Close']
    
    # Calculate middle band (SMA)
    middle_band = prices.rolling(window=window).mean()
    
    # Calculate standard deviation
    std = prices.rolling(window=window).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return upper_band, middle_band, lower_band


def calculate_weekly_bollinger_bands(daily_ohlc: pd.DataFrame, window: int = 4, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate weekly Bollinger Bands by first aggregating daily data to weekly
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Moving average window (for weekly data)
        num_std: Number of standard deviations for bands
        
    Returns:
        Tuple of (upper_band, middle_band, lower_band) for weekly data
    """
    # Aggregate daily data to weekly
    weekly_ohlc = aggregate_daily_to_weekly(daily_ohlc)
    prices = weekly_ohlc['Close']
    
    # Calculate middle band (SMA)
    middle_band = prices.rolling(window=window).mean()
    
    # Calculate standard deviation
    std = prices.rolling(window=window).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return upper_band, middle_band, lower_band


def calculate_bollinger_bands(daily_ohlc: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> Dict[str, Dict[str, pd.Series]]:
    """
    Calculate both daily and weekly Bollinger Bands
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Moving average window for daily calculation
        num_std: Number of standard deviations for bands
        
    Returns:
        Dictionary with daily and weekly Bollinger Bands data
    """
    # Calculate daily Bollinger Bands
    daily_upper, daily_middle, daily_lower = calculate_daily_bollinger_bands(daily_ohlc, window, num_std)
    
    # Calculate weekly Bollinger Bands
    weekly_upper, weekly_middle, weekly_lower = calculate_weekly_bollinger_bands(daily_ohlc, window // 5, num_std)
    
    return {
        'daily_bollinger_bands': {
            'upper': daily_upper,
            'middle': daily_middle,
            'lower': daily_lower
        },
        'weekly_bollinger_bands': {
            'upper': weekly_upper,
            'middle': weekly_middle,
            'lower': weekly_lower
        }
    }


def calculate_bollinger_band_width(upper_band: pd.Series, lower_band: pd.Series, middle_band: pd.Series) -> pd.Series:
    """
    Calculate Bollinger Band width
    
    Args:
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        middle_band: Middle Bollinger Band (SMA)
        
    Returns:
        Series of band widths
    """
    return (upper_band - lower_band) / middle_band


def calculate_bollinger_band_position(price: pd.Series, upper_band: pd.Series, lower_band: pd.Series) -> pd.Series:
    """
    Calculate position of price within Bollinger Bands (0-1 scale)
    
    Args:
        price: Current price
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        
    Returns:
        Series of positions (0 = lower band, 1 = upper band)
    """
    return (price - lower_band) / (upper_band - lower_band)


def get_bollinger_band_signals(prices: pd.Series, upper_band: pd.Series, lower_band: pd.Series) -> pd.Series:
    """
    Generate buy/sell signals based on Bollinger Bands
    
    Args:
        prices: Series of prices
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        
    Returns:
        Series of signals (1 for buy, -1 for sell, 0 for hold)
    """
    signals = pd.Series(0, index=prices.index)
    
    # Buy signal: price touches or goes below lower band
    buy_condition = prices <= lower_band
    
    # Sell signal: price touches or goes above upper band
    sell_condition = prices >= upper_band
    
    signals[buy_condition] = 1
    signals[sell_condition] = -1
    
    return signals


def is_bollinger_squeeze(upper_band: pd.Series, lower_band: pd.Series, middle_band: pd.Series, 
                        threshold: float = 0.1) -> pd.Series:
    """
    Identify Bollinger Band squeeze periods (low volatility)
    
    Args:
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        middle_band: Middle Bollinger Band
        threshold: Squeeze threshold (default 10%)
        
    Returns:
        Boolean series indicating squeeze periods
    """
    band_width = calculate_bollinger_band_width(upper_band, lower_band, middle_band)
    return band_width < threshold


def calculate_bollinger_band_percentile(upper_band: pd.Series, lower_band: pd.Series, 
                                      middle_band: pd.Series, window: int = 252) -> pd.Series:
    """
    Calculate Bollinger Band width percentile ranking
    
    Args:
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        middle_band: Middle Bollinger Band
        window: Window for percentile calculation
        
    Returns:
        Series of band width percentiles
    """
    band_width = calculate_bollinger_band_width(upper_band, lower_band, middle_band)
    return band_width.rolling(window=window).rank(pct=True)
