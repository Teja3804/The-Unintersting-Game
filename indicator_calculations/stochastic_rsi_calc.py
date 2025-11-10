"""
Stochastic RSI Calculation Module
Calculates Stochastic RSI indicator for stock analysis
Supports both daily and weekly timeframes
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
from .ohlc_aggregator import aggregate_daily_to_weekly


def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: Series of closing prices
        window: RSI calculation window
        
    Returns:
        Series of RSI values
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_stochastic(prices: pd.Series, window: int = 14) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate Stochastic Oscillator
    
    Args:
        prices: Series of closing prices
        window: Stochastic calculation window
        
    Returns:
        Tuple of (%K, %D) series
    """
    # For this implementation, we'll use the close prices as both high and low
    # In a real implementation, you'd need actual high and low prices
    low_min = prices.rolling(window=window).min()
    high_max = prices.rolling(window=window).max()
    
    k_percent = 100 * ((prices - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=3).mean()
    
    return k_percent, d_percent


def calculate_daily_stochastic_rsi(daily_ohlc: pd.DataFrame, rsi_window: int = 14, stoch_window: int = 14, 
                                 k_smooth: int = 3, d_smooth: int = 3) -> pd.DataFrame:
    """
    Calculate daily Stochastic RSI indicator
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        rsi_window: RSI calculation window
        stoch_window: Stochastic calculation window
        k_smooth: %K smoothing period
        d_smooth: %D smoothing period
        
    Returns:
        DataFrame with %K and %D values
    """
    prices = daily_ohlc['Close']
    
    # Calculate RSI
    rsi = calculate_rsi(prices, rsi_window)
    
    # Calculate Stochastic of RSI
    rsi_low = rsi.rolling(window=stoch_window).min()
    rsi_high = rsi.rolling(window=stoch_window).max()
    
    # Calculate %K
    stoch_k = 100 * ((rsi - rsi_low) / (rsi_high - rsi_low))
    
    # Smooth %K
    stoch_k_smooth = stoch_k.rolling(window=k_smooth).mean()
    
    # Calculate %D (smoothed %K)
    stoch_d = stoch_k_smooth.rolling(window=d_smooth).mean()
    
    return pd.DataFrame({
        '%K': stoch_k_smooth,
        '%D': stoch_d,
        'RSI': rsi
    })


def calculate_weekly_stochastic_rsi(daily_ohlc: pd.DataFrame, rsi_window: int = 14, stoch_window: int = 14, 
                                  k_smooth: int = 3, d_smooth: int = 3) -> pd.DataFrame:
    """
    Calculate weekly Stochastic RSI indicator by first aggregating daily data to weekly
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        rsi_window: RSI calculation window (for weekly data)
        stoch_window: Stochastic calculation window (for weekly data)
        k_smooth: %K smoothing period
        d_smooth: %D smoothing period
        
    Returns:
        DataFrame with weekly %K and %D values
    """
    # Aggregate daily data to weekly
    weekly_ohlc = aggregate_daily_to_weekly(daily_ohlc)
    prices = weekly_ohlc['Close']
    
    # Calculate RSI for weekly data
    rsi = calculate_rsi(prices, rsi_window)
    
    # Calculate Stochastic of RSI
    rsi_low = rsi.rolling(window=stoch_window).min()
    rsi_high = rsi.rolling(window=stoch_window).max()
    
    # Calculate %K
    stoch_k = 100 * ((rsi - rsi_low) / (rsi_high - rsi_low))
    
    # Smooth %K
    stoch_k_smooth = stoch_k.rolling(window=k_smooth).mean()
    
    # Calculate %D (smoothed %K)
    stoch_d = stoch_k_smooth.rolling(window=d_smooth).mean()
    
    return pd.DataFrame({
        '%K': stoch_k_smooth,
        '%D': stoch_d,
        'RSI': rsi
    })


def calculate_stochastic_rsi(daily_ohlc: pd.DataFrame, rsi_window: int = 14, stoch_window: int = 14, 
                           k_smooth: int = 3, d_smooth: int = 3) -> Dict[str, pd.DataFrame]:
    """
    Calculate both daily and weekly Stochastic RSI indicators
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        rsi_window: RSI calculation window
        stoch_window: Stochastic calculation window
        k_smooth: %K smoothing period
        d_smooth: %D smoothing period
        
    Returns:
        Dictionary with 'daily_stochastic_rsi' and 'weekly_stochastic_rsi' DataFrames
    """
    daily_stoch_rsi = calculate_daily_stochastic_rsi(daily_ohlc, rsi_window, stoch_window, k_smooth, d_smooth)
    weekly_stoch_rsi = calculate_weekly_stochastic_rsi(daily_ohlc, rsi_window, stoch_window, k_smooth, d_smooth)
    
    return {
        'daily_stochastic_rsi': daily_stoch_rsi,
        'weekly_stochastic_rsi': weekly_stoch_rsi
    }


def get_stochastic_rsi_signals(stoch_rsi_data: pd.DataFrame, 
                              overbought: float = 80, 
                              oversold: float = 20) -> pd.Series:
    """
    Generate buy/sell signals based on Stochastic RSI
    
    Args:
        stoch_rsi_data: DataFrame with %K and %D values
        overbought: Overbought threshold
        oversold: Oversold threshold
        
    Returns:
        Series of signals (1 for buy, -1 for sell, 0 for hold)
    """
    signals = pd.Series(0, index=stoch_rsi_data.index)
    
    k_values = stoch_rsi_data['%K']
    d_values = stoch_rsi_data['%D']
    
    # Buy signal: %K crosses above %D from oversold levels
    buy_condition = (k_values > d_values) & (k_values.shift(1) <= d_values.shift(1)) & (k_values < oversold)
    
    # Sell signal: %K crosses below %D from overbought levels
    sell_condition = (k_values < d_values) & (k_values.shift(1) >= d_values.shift(1)) & (k_values > overbought)
    
    signals[buy_condition] = 1
    signals[sell_condition] = -1
    
    return signals


def is_stochastic_rsi_oversold(stoch_rsi_data: pd.DataFrame, threshold: float = 20) -> pd.Series:
    """
    Check if Stochastic RSI is in oversold territory
    
    Args:
        stoch_rsi_data: DataFrame with %K and %D values
        threshold: Oversold threshold
        
    Returns:
        Boolean series indicating oversold conditions
    """
    return (stoch_rsi_data['%K'] < threshold) & (stoch_rsi_data['%D'] < threshold)


def is_stochastic_rsi_overbought(stoch_rsi_data: pd.DataFrame, threshold: float = 80) -> pd.Series:
    """
    Check if Stochastic RSI is in overbought territory
    
    Args:
        stoch_rsi_data: DataFrame with %K and %D values
        threshold: Overbought threshold
        
    Returns:
        Boolean series indicating overbought conditions
    """
    return (stoch_rsi_data['%K'] > threshold) & (stoch_rsi_data['%D'] > threshold)
