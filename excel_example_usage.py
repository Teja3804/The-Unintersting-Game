"""
Example: Using Excel Files with Trading Algorithm
This script demonstrates how to load stock data from Excel files and analyze them
"""

from excel_data_loader import ExcelDataLoader
from main_algorithm import StockAnalyzer
import os


def main():
    """
    Example workflow: Load Excel data and analyze stocks
    """
    print("="*60)
    print("EXCEL-BASED TRADING ALGORITHM EXAMPLE")
    print("="*60)
    
    # Step 1: Initialize Excel data loader
    print("\n[Step 1] Initializing Excel data loader...")
    data_directory = "data"  # Change this to your data directory path
    
    # Check if directory exists
    if not os.path.exists(data_directory):
        print(f"✗ Data directory not found: {data_directory}")
        print(f"  Please create the directory and add your Excel files")
        print(f"  Expected structure:")
        print(f"    Option 1: {data_directory}/STOCK_NAME_*.xlsx (all files in one folder)")
        print(f"    Option 2: {data_directory}/STOCK_NAME/*.xlsx (each stock in its own folder)")
        return
    
    try:
        loader = ExcelDataLoader(data_directory)
        print(f"✓ Data loader initialized with directory: {data_directory}")
    except Exception as e:
        print(f"✗ Error initializing data loader: {str(e)}")
        return
    
    # Step 2: Load stock data
    print("\n[Step 2] Loading stock data from Excel files...")
    
    # Option A: Load specific stocks
    stock_names = ["RELIANCE", "TCS", "INFY"]  # Replace with your stock names
    
    # Option B: Auto-detect stocks from filenames
    # stock_names = None  # Will auto-detect
    
    # Option C: Use folder structure (data/STOCK_NAME/*.xlsx)
    # stocks_data = loader.load_from_folder_structure()
    
    try:
        # Load all stocks
        stocks_data = loader.load_all_stocks(stock_names=stock_names, auto_detect=False)
        
        if not stocks_data:
            print("✗ No stock data loaded. Please check your Excel files.")
            return
        
        print(f"\n✓ Loaded data for {len(stocks_data)} stock(s)")
        for stock_name, df in stocks_data.items():
            print(f"  {stock_name}: {len(df)} rows, date range: {df['Date'].min()} to {df['Date'].max()}")
            
    except Exception as e:
        print(f"✗ Error loading stock data: {str(e)}")
        return
    
    # Step 3: Initialize analyzer
    print("\n[Step 3] Initializing stock analyzer...")
    analyzer = StockAnalyzer()
    print("✓ Analyzer initialized")
    
    # Step 4: Analyze stocks
    print("\n[Step 4] Analyzing stocks...")
    print("="*60)
    
    all_results = {}
    for stock_name, ohlc_data in stocks_data.items():
        try:
            print(f"\nAnalyzing {stock_name}...")
            result = analyzer.analyze_stock(ohlc_data, stock_name)
            all_results[stock_name] = result
            
            signals = result.get('trading_signals', [])
            print(f"✓ Analysis complete!")
            print(f"  Data points: {len(ohlc_data)}")
            print(f"  Signals detected: {len(signals)}")
            
            # Display signals
            if signals:
                print(f"\n  [TRADING SIGNALS for {stock_name}]")
                print("  " + "-" * 56)
                for i, signal in enumerate(signals[:5], 1):  # Show first 5 signals
                    print(f"\n  Signal {i}:")
                    print(f"    Case: {signal.get('case', 'N/A')}")
                    print(f"    Date: {signal.get('date', 'N/A')}")
                    print(f"    Entry Price: ₹{signal.get('entry_price', 0):.2f}")
                    print(f"    Stop Loss: ₹{signal.get('stop_loss', 0):.2f}")
                    print(f"    Target: ₹{signal.get('target', 0):.2f}")
                    if 'market_direction' in signal:
                        print(f"    Market Direction: {signal['market_direction']}")
                    if 'signal_strength' in signal:
                        print(f"    Signal Strength: {signal['signal_strength']}")
                
                if len(signals) > 5:
                    print(f"\n  ... and {len(signals) - 5} more signals")
            else:
                print(f"  No trading signals detected for {stock_name}")
                
        except Exception as e:
            print(f"✗ Error analyzing {stock_name}: {str(e)}")
            continue
    
    # Step 5: Summary
    print("\n" + "="*60)
    print("[SUMMARY]")
    print("-" * 60)
    total_signals = 0
    for stock_name, result in all_results.items():
        signal_count = len(result.get('trading_signals', []))
        total_signals += signal_count
        print(f"{stock_name}: {signal_count} signal(s) detected")
    
    print(f"\nTotal: {total_signals} signals across {len(all_results)} stock(s)")
    print("="*60)
    print("Example complete!")
    print("="*60)
    
    # Optional: Export results to CSV
    # You can add export functionality here if needed


if __name__ == "__main__":
    main()

