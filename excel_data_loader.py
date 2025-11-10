"""
Excel Data Loader
Reads stock data from Excel files and converts to OHLC DataFrame format
Supports multiple Excel sheets per stock
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import glob


class ExcelDataLoader:
    """
    Loads stock data from Excel files
    Supports multiple sheets per stock and combines them into a single DataFrame
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the Excel data loader
        
        Args:
            data_directory: Path to directory containing Excel files
        """
        self.data_directory = Path(data_directory)
        if not self.data_directory.exists():
            raise ValueError(f"Data directory not found: {data_directory}")
    
    def read_excel_file(self, file_path: Union[str, Path], 
                        sheet_name: Optional[Union[str, int]] = None,
                        combine_sheets: bool = True) -> pd.DataFrame:
        """
        Read Excel file(s) and convert to OHLC format
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet name or index to read (None reads all sheets)
            combine_sheets: If True and multiple sheets exist, combine them
        
        Returns:
            DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Read Excel file
            if sheet_name is not None:
                # Read specific sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                return self._normalize_dataframe(df)
            else:
                # Read all sheets
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')
                sheet_names = excel_file.sheet_names
                
                if len(sheet_names) == 1:
                    # Single sheet
                    df = pd.read_excel(file_path, sheet_name=sheet_names[0], engine='openpyxl')
                    return self._normalize_dataframe(df)
                elif combine_sheets:
                    # Multiple sheets - combine them
                    all_dataframes = []
                    for sheet in sheet_names:
                        df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
                        df = self._normalize_dataframe(df)
                        all_dataframes.append(df)
                    
                    # Combine and sort by date
                    combined_df = pd.concat(all_dataframes, ignore_index=True)
                    combined_df = combined_df.sort_values('Date').reset_index(drop=True)
                    # Remove duplicates based on Date
                    combined_df = combined_df.drop_duplicates(subset=['Date'], keep='last')
                    return combined_df
                else:
                    # Return first sheet only
                    df = pd.read_excel(file_path, sheet_name=sheet_names[0], engine='openpyxl')
                    return self._normalize_dataframe(df)
                    
        except Exception as e:
            raise ValueError(f"Error reading Excel file {file_path}: {str(e)}")
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize DataFrame to expected OHLC format
        
        Args:
            df: Raw DataFrame from Excel
        
        Returns:
            Normalized DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        """
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Store original column names for reference
        original_columns = df.columns.tolist()
        
        # Normalize column names (lowercase, strip whitespace)
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Common column name mappings (case-insensitive, after lowercase normalization)
        column_mappings = {
            'date': 'Date',
            'datetime': 'Date',
            'time': 'Date',
            'timestamp': 'Date',
            'open': 'Open',
            'o': 'Open',
            'high': 'High',
            'h': 'High',
            'low': 'Low',
            'l': 'Low',
            'close': 'Close',
            'c': 'Close',
            'price': 'Close',
            'volume': 'Volume',
            'vol': 'Volume',
            'v': 'Volume',
            # Additional mappings for common Excel formats (these will be ignored later)
            'prev. close': 'PrevClose',
            'prev close': 'PrevClose',
            'ltp': 'LTP',
            '52w h': '52WH',
            '52w l': '52WL',
            '52wh': '52WH',
            '52wl': '52WL',
            'value': 'Value',
            'no of trades': 'NoOfTrades',
            'no. of trades': 'NoOfTrades',
            'series': 'Series'
        }
        
        # Map columns
        for old_name, new_name in column_mappings.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Try to find Date column if not found
        if 'Date' not in df.columns:
            # Look for date-like columns
            for col in df.columns:
                if 'date' in col or 'time' in col or 'datetime' in col:
                    df = df.rename(columns={col: 'Date'})
                    break
        
        # Ensure Date column exists and is datetime
        if 'Date' not in df.columns:
            raise ValueError("Date column not found in Excel file. Please ensure your Excel file has a date column.")
        
        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Check for required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}. "
                           f"Found columns: {list(df.columns)}. "
                           f"Original columns were: {original_columns}")
        
        # Select only required columns (ignore unused columns like PrevClose, LTP, 52WH, Value, NoOfTrades, Series, etc.)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
        
        # Remove rows with missing dates
        df = df.dropna(subset=['Date'])
        
        # Sort by date
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Convert numeric columns
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing OHLC data
        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        
        return df
    
    def load_stock_data(self, stock_name: str, 
                       file_pattern: Optional[str] = None) -> pd.DataFrame:
        """
        Load all Excel files for a specific stock
        
        Args:
            stock_name: Name of the stock (used to match filenames)
            file_pattern: Optional pattern to match files (e.g., "RELIANCE*.xlsx")
        
        Returns:
            Combined DataFrame with all data for the stock
        """
        if file_pattern is None:
            # Default pattern: look for files containing stock name
            file_pattern = f"*{stock_name}*.xlsx"
        
        # Also check for .xls files
        patterns = [
            f"*{stock_name}*.xlsx",
            f"*{stock_name}*.xls",
            f"{stock_name}*.xlsx",
            f"{stock_name}*.xls"
        ]
        
        all_files = []
        for pattern in patterns:
            files = list(self.data_directory.glob(pattern))
            all_files.extend(files)
        
        # Remove duplicates
        all_files = list(set(all_files))
        
        if not all_files:
            raise FileNotFoundError(f"No Excel files found for stock: {stock_name} in {self.data_directory}")
        
        # Read and combine all files
        all_dataframes = []
        for file_path in all_files:
            try:
                df = self.read_excel_file(file_path, combine_sheets=True)
                all_dataframes.append(df)
                print(f"  ✓ Loaded {file_path.name} ({len(df)} rows)")
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {str(e)}")
        
        if not all_dataframes:
            raise ValueError(f"No valid data loaded for stock: {stock_name}")
        
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        combined_df = combined_df.sort_values('Date').reset_index(drop=True)
        # Remove duplicates based on Date
        combined_df = combined_df.drop_duplicates(subset=['Date'], keep='last')
        
        return combined_df
    
    def load_all_stocks(self, stock_names: Optional[List[str]] = None,
                       auto_detect: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Load data for multiple stocks
        
        Args:
            stock_names: List of stock names to load (None to auto-detect)
            auto_detect: If True, automatically detect stocks from filenames
        
        Returns:
            Dictionary with stock names as keys and DataFrames as values
        """
        stocks_data = {}
        
        if stock_names is None and auto_detect:
            # Auto-detect stocks from filenames
            excel_files = list(self.data_directory.glob("*.xlsx")) + list(self.data_directory.glob("*.xls"))
            
            # Extract unique stock names from filenames
            detected_stocks = set()
            for file_path in excel_files:
                # Try to extract stock name from filename
                # Assumes format like "STOCK_NAME_*.xlsx" or "STOCK_NAME.xlsx"
                name = file_path.stem  # filename without extension
                # Remove common suffixes
                for suffix in ['_data', '_ohlc', '_historical', '_daily', '_weekly']:
                    if name.endswith(suffix):
                        name = name[:-len(suffix)]
                detected_stocks.add(name)
            
            stock_names = sorted(list(detected_stocks))
            print(f"Auto-detected {len(stock_names)} stocks: {', '.join(stock_names)}")
        
        if stock_names is None:
            raise ValueError("No stock names provided and auto-detect failed")
        
        # Load each stock
        for stock_name in stock_names:
            try:
                print(f"\nLoading data for {stock_name}...")
                df = self.load_stock_data(stock_name)
                stocks_data[stock_name] = df
                print(f"✓ {stock_name}: {len(df)} rows loaded")
            except Exception as e:
                print(f"✗ Error loading {stock_name}: {str(e)}")
                continue
        
        return stocks_data
    
    def load_from_folder_structure(self, base_path: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Load data assuming folder structure: data/STOCK_NAME/*.xlsx
        
        Args:
            base_path: Base path (defaults to self.data_directory)
        
        Returns:
            Dictionary with stock names as keys and DataFrames as values
        """
        if base_path is None:
            base_path = self.data_directory
        
        base_path = Path(base_path)
        stocks_data = {}
        
        # Find all subdirectories (each represents a stock)
        for stock_dir in base_path.iterdir():
            if stock_dir.is_dir():
                stock_name = stock_dir.name
                print(f"\nLoading data for {stock_name} from folder...")
                
                # Find all Excel files in this directory
                excel_files = list(stock_dir.glob("*.xlsx")) + list(stock_dir.glob("*.xls"))
                
                if not excel_files:
                    print(f"  ✗ No Excel files found in {stock_dir}")
                    continue
                
                # Read and combine all files
                all_dataframes = []
                for file_path in excel_files:
                    try:
                        df = self.read_excel_file(file_path, combine_sheets=True)
                        all_dataframes.append(df)
                        print(f"  ✓ Loaded {file_path.name} ({len(df)} rows)")
                    except Exception as e:
                        print(f"  ✗ Error loading {file_path.name}: {str(e)}")
                
                if all_dataframes:
                    combined_df = pd.concat(all_dataframes, ignore_index=True)
                    combined_df = combined_df.sort_values('Date').reset_index(drop=True)
                    combined_df = combined_df.drop_duplicates(subset=['Date'], keep='last')
                    stocks_data[stock_name] = combined_df
                    print(f"✓ {stock_name}: {len(combined_df)} total rows")
        
        return stocks_data

