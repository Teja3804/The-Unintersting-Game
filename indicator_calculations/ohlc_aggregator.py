"""
OHLC Data Aggregation Module
Converts daily OHLC data to weekly OHLC data
"""

import pandas as pd
import numpy as np
from typing import Tuple


def aggregate_daily_to_weekly(daily_ohlc: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily OHLC data to weekly OHLC data
    
    Args:
        daily_ohlc: DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
    Returns:
        DataFrame with weekly OHLC data
    """
    # Ensure we have the right number of days for complete weeks
    total_days = len(daily_ohlc)
    days_to_ignore = total_days % 5
    
    if days_to_ignore > 0:
        # Remove the first 'days_to_ignore' days to get complete weeks
        daily_ohlc = daily_ohlc.iloc[days_to_ignore:].copy()
        print(f"Ignored first {days_to_ignore} days to ensure complete weeks")
    
    # Reset index after removing days
    daily_ohlc = daily_ohlc.reset_index(drop=True)
    
    # Create week groups (every 5 days)
    daily_ohlc['Week_Group'] = daily_ohlc.index // 5
    
    # Group by week and aggregate
    weekly_data = []
    
    for week_num, week_group in daily_ohlc.groupby('Week_Group'):
        if len(week_group) == 5:  # Only process complete weeks
            weekly_row = {
                'Date': week_group['Date'].iloc[-1],  # Last day of the week
                'Open': week_group['Open'].iloc[0],   # First day's open
                'High': week_group['High'].max(),     # Highest high of the week
                'Low': week_group['Low'].min(),       # Lowest low of the week
                'Close': week_group['Close'].iloc[-1], # Last day's close
                'Volume': week_group['Volume'].sum(),  # Total volume for the week
                'Week_Number': week_num + 1
            }
            weekly_data.append(weekly_row)
    
    weekly_ohlc = pd.DataFrame(weekly_data)
    return weekly_ohlc


def calculate_weekly_returns(weekly_ohlc: pd.DataFrame) -> pd.Series:
    """
    Calculate weekly returns from weekly OHLC data
    
    Args:
        weekly_ohlc: DataFrame with weekly OHLC data
        
    Returns:
        Series of weekly returns
    """
    return weekly_ohlc['Close'].pct_change().dropna()


def validate_ohlc_data(ohlc_data: pd.DataFrame) -> bool:
    """
    Validate OHLC data format and consistency
    
    Args:
        ohlc_data: DataFrame to validate
        
    Returns:
        Boolean indicating if data is valid
    """
    required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    # Check if all required columns exist
    if not all(col in ohlc_data.columns for col in required_columns):
        print(f"Missing required columns. Expected: {required_columns}")
        return False
    
    # Check for negative prices
    price_columns = ['Open', 'High', 'Low', 'Close']
    if (ohlc_data[price_columns] < 0).any().any():
        print("Found negative prices in OHLC data")
        return False
    
    # Check OHLC consistency (High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close)
    if not (ohlc_data['High'] >= ohlc_data['Low']).all():
        print("High prices are not consistently >= Low prices")
        return False
    
    if not (ohlc_data['High'] >= ohlc_data['Open']).all():
        print("High prices are not consistently >= Open prices")
        return False
    
    if not (ohlc_data['High'] >= ohlc_data['Close']).all():
        print("High prices are not consistently >= Close prices")
        return False
    
    if not (ohlc_data['Low'] <= ohlc_data['Open']).all():
        print("Low prices are not consistently <= Open prices")
        return False
    
    if not (ohlc_data['Low'] <= ohlc_data['Close']).all():
        print("Low prices are not consistently <= Close prices")
        return False
    
    return True


def get_data_summary(ohlc_data: pd.DataFrame, timeframe: str = "Daily") -> dict:
    """
    Get summary statistics for OHLC data
    
    Args:
        ohlc_data: DataFrame with OHLC data
        timeframe: Timeframe description ("Daily" or "Weekly")
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'timeframe': timeframe,
        'total_periods': len(ohlc_data),
        'date_range': {
            'start': ohlc_data['Date'].min(),
            'end': ohlc_data['Date'].max()
        },
        'price_range': {
            'min_close': ohlc_data['Close'].min(),
            'max_close': ohlc_data['Close'].max(),
            'avg_close': ohlc_data['Close'].mean()
        },
        'volume_stats': {
            'total_volume': ohlc_data['Volume'].sum(),
            'avg_volume': ohlc_data['Volume'].mean(),
            'max_volume': ohlc_data['Volume'].max()
        }
    }
    
    return summary
