# Excel Data Loading Guide

This guide explains how to organize and use Excel files with the trading algorithm.

## Overview

The system can now read stock data directly from Excel files instead of using API calls. Each stock can have multiple Excel files (5-10 files per stock), and the system will automatically combine them.

## Excel File Format

Your Excel files should contain OHLC (Open, High, Low, Close) data with Volume. The system is flexible with column names and will automatically detect them.

### Required Columns

Your Excel files must contain the following data (column names can vary):

| Required Data | Accepted Column Names |
|--------------|----------------------|
| Date | `Date`, `date`, `DateTime`, `datetime`, `Time`, `time`, `Timestamp`, `timestamp` |
| Open | `Open`, `open`, `O` |
| High | `High`, `high`, `H` |
| Low | `Low`, `low`, `L` |
| Close | `Close`, `close`, `C`, `Price`, `price` |
| Volume | `Volume`, `volume`, `Vol`, `vol`, `V` |

### Example Excel Structure

```
| Date       | Open  | High  | Low   | Close | Volume |
|------------|-------|-------|-------|-------|--------|
| 2024-01-01 | 100.5 | 102.3 | 99.8  | 101.2 | 1000000|
| 2024-01-02 | 101.2 | 103.1 | 100.5 | 102.8 | 1200000|
| 2024-01-03 | 102.8 | 104.2 | 101.9 | 103.5 | 1100000|
```

## File Organization

You can organize your Excel files in two ways:

### Option 1: Single Folder (Recommended for your use case)

Place all Excel files in a single `data/` folder. Files should be named to include the stock name:

```
data/
├── RELIANCE_2024_Q1.xlsx
├── RELIANCE_2024_Q2.xlsx
├── RELIANCE_2024_Q3.xlsx
├── TCS_2024_Q1.xlsx
├── TCS_2024_Q2.xlsx
├── INFY_2024_Q1.xlsx
└── ...
```

**Naming Convention:**
- Files should contain the stock name (e.g., "RELIANCE", "TCS")
- The system will automatically group files by stock name
- Each Excel file can have multiple sheets - they will be combined automatically

### Option 2: Folder Structure

Organize files by stock name in separate folders:

```
data/
├── RELIANCE/
│   ├── sheet1.xlsx
│   ├── sheet2.xlsx
│   └── sheet3.xlsx
├── TCS/
│   ├── sheet1.xlsx
│   └── sheet2.xlsx
└── INFY/
    └── sheet1.xlsx
```

## Multiple Sheets Per File

If your Excel files contain multiple sheets, the system will:
1. Read all sheets from each file
2. Combine them into a single dataset
3. Remove duplicate dates (keeping the last entry)
4. Sort by date chronologically

## Usage Examples

### Basic Usage

```python
from excel_data_loader import ExcelDataLoader
from main_algorithm import StockAnalyzer

# Initialize loader
loader = ExcelDataLoader("data")  # Path to your data folder

# Load a specific stock
reliance_data = loader.load_stock_data("RELIANCE")

# Analyze the stock
analyzer = StockAnalyzer()
result = analyzer.analyze_stock(reliance_data, "RELIANCE")
signals = result['trading_signals']
```

### Load Multiple Stocks

```python
# Load multiple stocks
stocks_data = loader.load_all_stocks(
    stock_names=["RELIANCE", "TCS", "INFY"],
    auto_detect=False
)

# Or auto-detect stocks from filenames
stocks_data = loader.load_all_stocks(auto_detect=True)

# Analyze all stocks
analyzer = StockAnalyzer()
results = analyzer.analyze_multiple_stocks(stocks_data)
```

### Using Folder Structure

```python
# If using folder structure (data/STOCK_NAME/*.xlsx)
stocks_data = loader.load_from_folder_structure()
```

## Running the Example

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Organize your Excel files in a `data/` folder (or specify your path)

3. Update `excel_example_usage.py` with your stock names:
```python
stock_names = ["RELIANCE", "TCS", "INFY"]  # Your stock names
```

4. Run the example:
```bash
python excel_example_usage.py
```

## Data Validation

The system will:
- ✅ Automatically detect and map column names
- ✅ Convert dates to datetime format
- ✅ Remove rows with missing data
- ✅ Sort data chronologically
- ✅ Remove duplicate dates
- ✅ Combine multiple sheets/files per stock

## Troubleshooting

### "Date column not found"
- Ensure your Excel file has a date column with one of the accepted names
- Check that dates are in a recognizable format

### "Missing required columns"
- Verify your Excel file has Open, High, Low, Close, and Volume columns
- Column names are case-insensitive

### "No Excel files found for stock"
- Check that your file names contain the stock name
- Verify the data directory path is correct
- Ensure files have `.xlsx` or `.xls` extension

### "Error reading Excel file"
- Make sure the file is not corrupted
- Check that the file is not open in another program
- Verify the file format is supported (Excel 2007+)

## Tips

1. **File Naming**: Use consistent naming (e.g., `STOCK_NAME_PERIOD.xlsx`)
2. **Date Format**: Use standard date formats (YYYY-MM-DD recommended)
3. **Data Quality**: Ensure no missing values in OHLC columns
4. **Volume**: Volume can be 0 but should not be negative
5. **Multiple Files**: The system handles combining multiple files per stock automatically

## Support

For issues or questions, check:
- Excel file format matches the requirements
- Column names are recognized
- File paths are correct
- Data directory exists and is accessible

