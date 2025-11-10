"""
Volatility Calculation Module
Calculates various volatility measures for stock price data
Supports both daily and weekly timeframes
"""

import pandas as pd
import numpy as np
from typing import Union, Dict
from .ohlc_aggregator import aggregate_daily_to_weekly


def calculate_daily_volatility(daily_ohlc: pd.DataFrame, window: int = 20, method: str = 'std') -> pd.Series:
    """
    Calculate daily volatility of stock prices
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Rolling window size for calculation
        method: Method to calculate volatility ('std', 'garman_klass', 'parkinson')
        
    Returns:
        Series of daily volatility values
    """
    prices = daily_ohlc['Close']
    
    if method == 'std':
        # Simple standard deviation of returns
        returns = prices.pct_change().dropna()
        volatility = returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        return volatility
    
    elif method == 'garman_klass':
        # Garman-Klass volatility estimator using OHLC data
        high = daily_ohlc['High']
        low = daily_ohlc['Low']
        open_price = daily_ohlc['Open']
        close = daily_ohlc['Close']
        
        # Garman-Klass formula
        gk = 0.5 * (np.log(high / low) ** 2) - (2 * np.log(2) - 1) * (np.log(close / open_price) ** 2)
        volatility = gk.rolling(window=window).mean() * np.sqrt(252)
        return volatility
    
    elif method == 'parkinson':
        # Parkinson volatility estimator using High-Low data
        high = daily_ohlc['High']
        low = daily_ohlc['Low']
        
        # Parkinson formula
        parkinson = (1 / (4 * np.log(2))) * (np.log(high / low) ** 2)
        volatility = parkinson.rolling(window=window).mean() * np.sqrt(252)
        return volatility
    
    else:
        raise ValueError("Method must be 'std', 'garman_klass', or 'parkinson'")


def calculate_weekly_volatility(daily_ohlc: pd.DataFrame, window: int = 4, method: str = 'std') -> pd.Series:
    """
    Calculate weekly volatility by first aggregating daily data to weekly
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Rolling window size for weekly calculation (default 4 weeks)
        method: Method to calculate volatility ('std', 'garman_klass', 'parkinson')
        
    Returns:
        Series of weekly volatility values
    """
    # Aggregate daily data to weekly
    weekly_ohlc = aggregate_daily_to_weekly(daily_ohlc)
    
    if method == 'std':
        # Calculate weekly returns and volatility
        weekly_returns = weekly_ohlc['Close'].pct_change().dropna()
        volatility = weekly_returns.rolling(window=window).std() * np.sqrt(52)  # Annualized for weekly data
        return volatility
    
    elif method == 'garman_klass':
        # Garman-Klass volatility for weekly data
        high = weekly_ohlc['High']
        low = weekly_ohlc['Low']
        open_price = weekly_ohlc['Open']
        close = weekly_ohlc['Close']
        
        gk = 0.5 * (np.log(high / low) ** 2) - (2 * np.log(2) - 1) * (np.log(close / open_price) ** 2)
        volatility = gk.rolling(window=window).mean() * np.sqrt(52)
        return volatility
    
    elif method == 'parkinson':
        # Parkinson volatility for weekly data
        high = weekly_ohlc['High']
        low = weekly_ohlc['Low']
        
        parkinson = (1 / (4 * np.log(2))) * (np.log(high / low) ** 2)
        volatility = parkinson.rolling(window=window).mean() * np.sqrt(52)
        return volatility
    
    else:
        raise ValueError("Method must be 'std', 'garman_klass', or 'parkinson'")


def calculate_volatility(daily_ohlc: pd.DataFrame, window: int = 20, method: str = 'std') -> Dict[str, pd.Series]:
    """
    Calculate both daily and weekly volatility
    
    Args:
        daily_ohlc: DataFrame with daily OHLC data
        window: Rolling window size for daily calculation
        method: Method to calculate volatility
        
    Returns:
        Dictionary with 'daily_volatility' and 'weekly_volatility' series
    """
    daily_vol = calculate_daily_volatility(daily_ohlc, window, method)
    weekly_vol = calculate_weekly_volatility(daily_ohlc, window // 5, method)  # Adjust window for weekly
    
    return {
        'daily_volatility': daily_vol,
        'weekly_volatility': weekly_vol
    }


def calculate_historical_volatility(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate historical volatility using standard deviation of returns
    
    Args:
        prices: Series of closing prices
        window: Rolling window size
        
    Returns:
        Series of historical volatility values
    """
    returns = prices.pct_change().dropna()
    hist_vol = returns.rolling(window=window).std() * np.sqrt(252)
    return hist_vol


def calculate_volatility_ratio(current_vol: float, historical_vol: float) -> float:
    """
    Calculate volatility ratio (current vs historical)
    
    Args:
        current_vol: Current volatility value
        historical_vol: Historical average volatility
        
    Returns:
        Volatility ratio
    """
    if historical_vol == 0:
        return 0
    return current_vol / historical_vol


def is_high_volatility(volatility: pd.Series, threshold: float = 0.3) -> pd.Series:
    """
    Identify periods of high volatility
    
    Args:
        volatility: Series of volatility values
        threshold: Volatility threshold (default 30%)
        
    Returns:
        Boolean series indicating high volatility periods
    """
    return volatility > threshold


def calculate_volatility_percentile(volatility: pd.Series, window: int = 252) -> pd.Series:
    """
    Calculate volatility percentile ranking
    
    Args:
        volatility: Series of volatility values
        window: Window for percentile calculation
        
    Returns:
        Series of volatility percentiles
    """
    return volatility.rolling(window=window).rank(pct=True)
