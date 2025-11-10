# Stock Market Analysis Algorithm

A comprehensive stock market analysis tool that uses OHLC (Open, High, Low, Close) data with volume to generate trading signals using multiple technical indicators.

## Features

- **Dual Timeframe Analysis**: Calculates indicators for both daily and weekly timeframes
- **Multiple Technical Indicators**:
  - Volatility (Daily & Weekly)
  - Stochastic RSI (Daily & Weekly)
  - Bollinger Bands (Daily & Weekly)
  - VWAP (Volume Weighted Average Price) (Daily & Weekly)
- **Intelligent Signal Generation**: Combines multiple indicators with signal strength scoring
- **OHLC Data Aggregation**: Automatically converts daily data to weekly data
- **API Ready**: Designed for integration with real-time market data APIs

## Project Structure

```
The Interest Game/
├── main_algorithm.py              # Main algorithm class
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── indicator_calculations/       # Indicator calculation modules
    ├── __init__.py
    ├── ohlc_aggregator.py        # OHLC data aggregation utilities
    ├── volatility_calc.py        # Volatility calculations
    ├── stochastic_rsi_calc.py    # Stochastic RSI calculations
    ├── bollinger_bands_calc.py   # Bollinger Bands calculations
    └── vwap_calc.py              # VWAP calculations
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from main_algorithm import StockAnalyzer
import pandas as pd

# Create your OHLC data
ohlc_data = pd.DataFrame({
    'Date': [...],      # Date column
    'Open': [...],      # Opening prices
    'High': [...],      # High prices
    'Low': [...],       # Low prices
    'Close': [...],     # Closing prices
    'Volume': [...]     # Volume data
})

# Initialize analyzer
analyzer = StockAnalyzer()

# Analyze single stock
result = analyzer.analyze_stock(ohlc_data, "STOCK_NAME")

# Get trading signals
signals = result['signals']
print(f"Generated {len(signals)} trading signals")
```

### Multiple Stocks Analysis

```python
# Prepare data for multiple stocks
stocks_data = {
    "AAPL": aapl_ohlc_data,
    "GOOGL": googl_ohlc_data,
    "MSFT": msft_ohlc_data
}

# Analyze all stocks
results = analyzer.analyze_multiple_stocks(stocks_data)

# Export to CSV
analyzer.export_signals_to_csv(results, "trading_signals.csv")
```

### Running the Algorithm

```bash
python main_algorithm.py
```

## Input Data Format

The algorithm expects OHLC data in the following format:

| Column | Type | Description |
|--------|------|-------------|
| Date | datetime | Trading date |
| Open | float | Opening price |
| High | float | Highest price of the day |
| Low | float | Lowest price of the day |
| Close | float | Closing price |
| Volume | int | Trading volume |

## Output Format

The algorithm generates trading signals with the following information:

| Field | Type | Description |
|-------|------|-------------|
| Date | datetime | Signal date |
| Stock_Name | string | Stock symbol |
| Direction | string | "BUY" or "SELL" |
| Target | float | Target price |
| Stop_Loss | float | Stop loss price |
| Time | string | Signal generation time |
| Current_Price | float | Current stock price |
| Signal_Strength | int | Signal strength score |
| Daily_Volatility | float | Daily volatility value |
| Weekly_Volatility | float | Weekly volatility value |
| Daily_Stochastic_K | float | Daily Stochastic %K |
| Daily_Stochastic_D | float | Daily Stochastic %D |
| Weekly_Stochastic_K | float | Weekly Stochastic %K |
| Weekly_Stochastic_D | float | Weekly Stochastic %D |
| Daily_VWAP | float | Daily VWAP value |
| Weekly_VWAP | float | Weekly VWAP value |

## Technical Indicators

### Volatility
- **Daily Volatility**: Calculated using rolling standard deviation of returns
- **Weekly Volatility**: Calculated from weekly aggregated data
- **Methods**: Standard deviation, Garman-Klass, Parkinson

### Stochastic RSI
- **Daily Stochastic RSI**: RSI-based stochastic oscillator for daily data
- **Weekly Stochastic RSI**: RSI-based stochastic oscillator for weekly data
- **Parameters**: RSI window (14), Stochastic window (14), Smoothing periods

### Bollinger Bands
- **Daily Bollinger Bands**: 20-period moving average with 2 standard deviations
- **Weekly Bollinger Bands**: 4-period moving average with 2 standard deviations
- **Components**: Upper band, Middle band (SMA), Lower band

### VWAP (Volume Weighted Average Price)
- **Daily VWAP**: Volume-weighted average price for daily data
- **Weekly VWAP**: Volume-weighted average price for weekly data
- **Calculation**: Uses typical price (HLC/3) weighted by volume

## Signal Generation Logic

The algorithm uses a signal strength scoring system:

1. **Daily Indicators**: Primary signals from daily timeframe
2. **Weekly Confirmation**: Weekly indicators provide confirmation
3. **Signal Strength**: Combines multiple indicator signals
4. **Volatility Filter**: Reduces signal strength during high volatility periods
5. **Threshold**: Requires signal strength ≥ 2 for BUY or ≤ -2 for SELL

## Weekly Data Aggregation

- Automatically handles incomplete weeks by ignoring excess days
- For 10002 days of data, ignores first 2 days to get 2000 complete weeks
- Aggregates OHLC data: Open (first day), High (max), Low (min), Close (last day)
- Sums volume for the week

## Example Output

```
Signal 1:
  Date: 2024-01-15
  Direction: BUY
  Current Price: $105.50
  Target: $110.78
  Stop Loss: $102.34
  Signal Strength: 3
  Daily Volatility: 0.0234
  Weekly Volatility: 0.0187
```

## Requirements

- Python 3.7+
- pandas >= 1.3.0
- numpy >= 1.21.0
- scipy >= 1.7.0

## License

This project is for educational and research purposes. Please ensure compliance with your local regulations when using for actual trading.
