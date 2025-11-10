"""
VWAP (Volume Weighted Average Price) Calculation Module
Calculates VWAP indicator for stock analysis
Supports both daily and weekly timeframes
"""

import pandas as pd
import numpy as np
from typing import Dict
from .ohlc_aggregator import aggregate_daily_to_weekly


def calculate_daily_vwap(daily_ohlc: pd.DataFrame, window: int = None) -> pd.Series:
    """
    Calculate daily VWAP (Volume Weighted Average Price)
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Rolling window for VWAP calculation (None for cumulative)
        
    Returns:
        Series of VWAP values
    """
    # Calculate typical price (HLC/3)
    typical_price = (daily_ohlc['High'] + daily_ohlc['Low'] + daily_ohlc['Close']) / 3
    
    # Calculate volume-weighted price
    volume_price = typical_price * daily_ohlc['Volume']
    
    if window is None:
        # Cumulative VWAP
        cumulative_volume = daily_ohlc['Volume'].cumsum()
        cumulative_volume_price = volume_price.cumsum()
        vwap = cumulative_volume_price / cumulative_volume
    else:
        # Rolling VWAP
        rolling_volume = daily_ohlc['Volume'].rolling(window=window).sum()
        rolling_volume_price = volume_price.rolling(window=window).sum()
        vwap = rolling_volume_price / rolling_volume
    
    return vwap


def calculate_weekly_vwap(daily_ohlc: pd.DataFrame, window: int = None) -> pd.Series:
    """
    Calculate weekly VWAP by first aggregating daily data to weekly
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Rolling window for VWAP calculation (None for cumulative)
        
    Returns:
        Series of weekly VWAP values
    """
    # Aggregate daily data to weekly
    weekly_ohlc = aggregate_daily_to_weekly(daily_ohlc)
    
    # Calculate typical price (HLC/3)
    typical_price = (weekly_ohlc['High'] + weekly_ohlc['Low'] + weekly_ohlc['Close']) / 3
    
    # Calculate volume-weighted price
    volume_price = typical_price * weekly_ohlc['Volume']
    
    if window is None:
        # Cumulative VWAP
        cumulative_volume = weekly_ohlc['Volume'].cumsum()
        cumulative_volume_price = volume_price.cumsum()
        vwap = cumulative_volume_price / cumulative_volume
    else:
        # Rolling VWAP
        rolling_volume = weekly_ohlc['Volume'].rolling(window=window).sum()
        rolling_volume_price = volume_price.rolling(window=window).sum()
        vwap = rolling_volume_price / rolling_volume
    
    return vwap


def calculate_vwap(daily_ohlc: pd.DataFrame, window: int = None) -> Dict[str, pd.Series]:
    """
    Calculate both daily and weekly VWAP
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Rolling window for VWAP calculation (None for cumulative)
        
    Returns:
        Dictionary with 'daily_vwap' and 'weekly_vwap' series
    """
    daily_vwap = calculate_daily_vwap(daily_ohlc, window)
    weekly_vwap = calculate_weekly_vwap(daily_ohlc, window)
    
    return {
        'daily_vwap': daily_vwap,
        'weekly_vwap': weekly_vwap
    }


def calculate_vwap_deviation(price: pd.Series, vwap: pd.Series) -> pd.Series:
    """
    Calculate deviation of price from VWAP
    
    Args:
        price: Current price
        vwap: VWAP value
        
    Returns:
        Series of deviations (percentage)
    """
    return ((price - vwap) / vwap) * 100


def get_vwap_signals(prices: pd.Series, vwap: pd.Series, threshold: float = 0.02) -> pd.Series:
    """
    Generate buy/sell signals based on VWAP
    
    Args:
        prices: Series of prices
        vwap: VWAP values
        threshold: Deviation threshold for signals (default 2%)
        
    Returns:
        Series of signals (1 for buy, -1 for sell, 0 for hold)
    """
    signals = pd.Series(0, index=prices.index)
    
    # Calculate deviation from VWAP
    deviation = calculate_vwap_deviation(prices, vwap)
    
    # Buy signal: price significantly below VWAP
    buy_condition = deviation < -threshold
    
    # Sell signal: price significantly above VWAP
    sell_condition = deviation > threshold
    
    signals[buy_condition] = 1
    signals[sell_condition] = -1
    
    return signals


def calculate_vwap_bands(vwap: pd.Series, std_multiplier: float = 2.0, window: int = 20) -> Dict[str, pd.Series]:
    """
    Calculate VWAP bands (VWAP ± standard deviation)
    
    Args:
        vwap: VWAP values
        std_multiplier: Standard deviation multiplier
        window: Window for standard deviation calculation
        
    Returns:
        Dictionary with upper and lower VWAP bands
    """
    # Calculate standard deviation of price deviations from VWAP
    # This is a simplified approach - in practice, you'd calculate std of price differences
    vwap_std = vwap.rolling(window=window).std()
    
    upper_band = vwap + (vwap_std * std_multiplier)
    lower_band = vwap - (vwap_std * std_multiplier)
    
    return {
        'upper_band': upper_band,
        'lower_band': lower_band
    }


def is_price_above_vwap(prices: pd.Series, vwap: pd.Series) -> pd.Series:
    """
    Check if price is above VWAP
    
    Args:
        prices: Series of prices
        vwap: VWAP values
        
    Returns:
        Boolean series indicating if price is above VWAP
    """
    return prices > vwap


def is_price_below_vwap(prices: pd.Series, vwap: pd.Series) -> pd.Series:
    """
    Check if price is below VWAP
    
    Args:
        prices: Series of prices
        vwap: VWAP values
        
    Returns:
        Boolean series indicating if price is below VWAP
    """
    return prices < vwap


def calculate_vwap_trend(vwap: pd.Series, window: int = 5) -> pd.Series:
    """
    Calculate VWAP trend direction
    
    Args:
        vwap: VWAP values
        window: Window for trend calculation
        
    Returns:
        Series of trend values (1 for uptrend, -1 for downtrend, 0 for sideways)
    """
    vwap_ma = vwap.rolling(window=window).mean()
    trend = pd.Series(0, index=vwap.index)
    
    # Uptrend: current VWAP > moving average
    uptrend = vwap > vwap_ma
    # Downtrend: current VWAP < moving average
    downtrend = vwap < vwap_ma
    
    trend[uptrend] = 1
    trend[downtrend] = -1
    
    return trend
