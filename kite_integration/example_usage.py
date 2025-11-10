"""
Example: Using Kite Connect with Trading Algorithm
This script demonstrates how to connect to Kite Connect and analyze stocks
"""

from kite_integration.kite_auth_helper import quick_authenticate
from kite_integration.kite_data_fetcher import KiteDataFetcher


def main():
    """
    Example workflow: Authenticate, fetch data, and analyze
    """
    print("="*60)
    print("KITE CONNECT TRADING ALGORITHM EXAMPLE")
    print("="*60)
    
    # Step 1: Authenticate with Kite Connect
    print("\n[Step 1] Authenticating with Kite Connect...")
    try:
        kite = quick_authenticate("kite_config.py")
        print("✓ Authentication successful!")
    except FileNotFoundError:
        print("✗ Config file not found!")
        print("  Please create kite_config.py from kite_config_example.py")
        return
    except Exception as e:
        print(f"✗ Authentication failed: {str(e)}")
        return
    
    # Step 2: Initialize data fetcher
    print("\n[Step 2] Initializing data fetcher...")
    fetcher = KiteDataFetcher(kite)
    
    # Step 3: Fetch and analyze a stock
    print("\n[Step 3] Fetching and analyzing RELIANCE...")
    try:
        result = fetcher.fetch_and_analyze(
            exchange="NSE",
            symbol="RELIANCE",
            days=100  # Fetch last 100 days
        )
        
        print(f"\n✓ Analysis complete!")
        print(f"  Symbol: {result['symbol']}")
        print(f"  Data points: {len(result['ohlc_data'])}")
        print(f"  Signals detected: {len(result['signals'])}")
        
        # Display signals
        if result['signals']:
            print("\n[TRADING SIGNALS]")
            print("-" * 60)
            for i, signal in enumerate(result['signals'], 1):
                print(f"\nSignal {i}:")
                print(f"  Case: {signal['case']}")
                print(f"  Date: {signal.get('date', 'N/A')}")
                print(f"  Entry Price: ₹{signal['entry_price']:.2f}")
                print(f"  Stop Loss: ₹{signal['stop_loss']:.2f}")
                print(f"  Target: ₹{signal['target']:.2f}")
                if 'market_direction' in signal:
                    print(f"  Market Direction: {signal['market_direction']}")
                if 'stoch_rsi' in signal:
                    print(f"  Stochastic RSI: {signal['stoch_rsi']:.2f}")
        else:
            print("\nNo trading signals detected for this period.")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Step 4: Example - Analyze multiple stocks
    print("\n" + "="*60)
    print("[Step 4] Analyzing multiple stocks...")
    symbols = ["RELIANCE", "TCS", "INFY"]
    
    try:
        results = fetcher.fetch_multiple_symbols(symbols, exchange="NSE", days=100)
        
        print("\n[SUMMARY]")
        print("-" * 60)
        for symbol, result in results.items():
            if 'error' in result:
                print(f"{symbol}: Error - {result['error']}")
            else:
                signal_count = len(result.get('signals', []))
                print(f"{symbol}: {signal_count} signal(s) detected")
                
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Example complete!")
    print("="*60)


if __name__ == "__main__":
    main()

