"""
Kite Connect API Integration Module
Handles authentication, data fetching, and order placement with Zerodha Kite Connect
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException


class KiteConnector:
    """
    Wrapper class for Kite Connect API integration
    """
    
    def __init__(self, api_key: str, api_secret: str, redirect_url: str = "http://127.0.0.1:8000"):
        """
        Initialize Kite Connect connector
        
        Args:
            api_key: Your Kite Connect API key
            api_secret: Your Kite Connect API secret
            redirect_url: Redirect URL registered in Kite Developer Portal
                         Default: http://127.0.0.1:8000 (for local testing)
                         For production: Use HTTPS URL like https://yourdomain.com/callback
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_url = redirect_url
        self.kite = KiteConnect(api_key=api_key)
        self.access_token = None
        self.user_id = None
        
    def get_login_url(self) -> str:
        """
        Generate login URL for OAuth authentication
        
        Returns:
            Login URL that user needs to visit
        """
        return self.kite.login_url()
    
    def generate_session(self, request_token: str) -> Dict:
        """
        Generate access token from request token after user authentication
        
        Args:
            request_token: Request token received from redirect URL after login
            
        Returns:
            Dictionary with access_token and user data
        """
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data['access_token']
            self.user_id = data['user_id']
            self.kite.set_access_token(self.access_token)
            return data
        except KiteException as e:
            raise Exception(f"Failed to generate session: {str(e)}")
    
    def set_access_token(self, access_token: str):
        """
        Set access token directly (useful if you've stored it previously)
        
        Args:
            access_token: Previously obtained access token
        """
        self.access_token = access_token
        self.kite.set_access_token(access_token)
        # Get user profile to verify token
        profile = self.kite.profile()
        self.user_id = profile['user_id']
    
    def get_ohlc_data(self, instrument_token: str, from_date: datetime, to_date: datetime, 
                     interval: str = "day", continuous: bool = False) -> pd.DataFrame:
        """
        Fetch OHLC data for a given instrument
        
        Args:
            instrument_token: Kite instrument token (e.g., "256265" for NIFTY 50)
            from_date: Start date for data
            to_date: End date for data
            interval: Data interval - "minute", "3minute", "5minute", "10minute", 
                     "15minute", "30minute", "60minute", "day"
            continuous: Whether to return continuous contract data
            
        Returns:
            DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            # Fetch historical data
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
                continuous=continuous
            )
            
            if not data:
                return pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['date'])
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Select and reorder columns
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df = df.sort_values('Date').reset_index(drop=True)
            
            return df
            
        except KiteException as e:
            raise Exception(f"Failed to fetch OHLC data: {str(e)}")
    
    def get_instrument_token(self, exchange: str, symbol: str) -> Optional[str]:
        """
        Get instrument token for a given exchange and symbol
        
        Args:
            exchange: Exchange name (e.g., "NSE", "BSE", "NFO")
            symbol: Trading symbol (e.g., "RELIANCE", "NIFTY50")
            
        Returns:
            Instrument token or None if not found
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            instruments = self.kite.instruments(exchange)
            for instrument in instruments:
                if instrument['tradingsymbol'] == symbol:
                    return str(instrument['instrument_token'])
            return None
        except KiteException as e:
            raise Exception(f"Failed to fetch instruments: {str(e)}")
    
    def search_instruments(self, query: str, exchange: str = None) -> List[Dict]:
        """
        Search for instruments by name or symbol
        
        Args:
            query: Search query (symbol or company name)
            exchange: Optional exchange filter (e.g., "NSE", "BSE")
            
        Returns:
            List of matching instruments
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            if exchange:
                instruments = self.kite.instruments(exchange)
            else:
                # Search in common exchanges
                instruments = []
                for exch in ["NSE", "BSE", "NFO"]:
                    try:
                        instruments.extend(self.kite.instruments(exch))
                    except:
                        continue
            
            # Filter by query
            query_lower = query.lower()
            results = []
            for instrument in instruments:
                if (query_lower in instrument['tradingsymbol'].lower() or 
                    query_lower in instrument['name'].lower()):
                    results.append(instrument)
            
            return results
        except KiteException as e:
            raise Exception(f"Failed to search instruments: {str(e)}")
    
    def place_order(self, variety: str, exchange: str, tradingsymbol: str, 
                   transaction_type: str, quantity: int, order_type: str = "MARKET",
                   product: str = "MIS", price: float = None, trigger_price: float = None,
                   stoploss: float = None, squareoff: float = None) -> Dict:
        """
        Place an order
        
        Args:
            variety: Order variety - "regular", "amo", "iceberg", "co"
            exchange: Exchange name (e.g., "NSE", "BSE")
            tradingsymbol: Trading symbol
            transaction_type: "BUY" or "SELL"
            quantity: Order quantity
            order_type: "MARKET", "LIMIT", "SL", "SL-M"
            product: "MIS" (Intraday), "CNC" (Delivery), "NRML" (Carry Forward)
            price: Price for LIMIT orders
            trigger_price: Trigger price for SL orders
            stoploss: Stop loss price
            squareoff: Square off price
            
        Returns:
            Order response dictionary
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            order_params = {
                "variety": variety,
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "order_type": order_type,
                "product": product
            }
            
            if price:
                order_params["price"] = price
            if trigger_price:
                order_params["trigger_price"] = trigger_price
            if stoploss:
                order_params["stoploss"] = stoploss
            if squareoff:
                order_params["squareoff"] = squareoff
            
            order_id = self.kite.place_order(**order_params)
            return {"order_id": order_id, "status": "success"}
            
        except KiteException as e:
            raise Exception(f"Failed to place order: {str(e)}")
    
    def get_profile(self) -> Dict:
        """
        Get user profile information
        
        Returns:
            User profile dictionary
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            return self.kite.profile()
        except KiteException as e:
            raise Exception(f"Failed to get profile: {str(e)}")
    
    def get_positions(self) -> Dict:
        """
        Get current positions
        
        Returns:
            Positions dictionary
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            return self.kite.positions()
        except KiteException as e:
            raise Exception(f"Failed to get positions: {str(e)}")
    
    def get_orders(self) -> List[Dict]:
        """
        Get order history
        
        Returns:
            List of orders
        """
        if not self.access_token:
            raise Exception("Access token not set. Please authenticate first.")
        
        try:
            return self.kite.orders()
        except KiteException as e:
            raise Exception(f"Failed to get orders: {str(e)}")


def save_access_token(access_token: str, filepath: str = "kite_access_token.txt"):
    """
    Save access token to file for future use
    
    Args:
        access_token: Access token to save
        filepath: Path to save the token
    """
    with open(filepath, 'w') as f:
        f.write(access_token)


def load_access_token(filepath: str = "kite_access_token.txt") -> Optional[str]:
    """
    Load access token from file
    
    Args:
        filepath: Path to token file
        
    Returns:
        Access token or None if file doesn't exist
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read().strip()
    return None

