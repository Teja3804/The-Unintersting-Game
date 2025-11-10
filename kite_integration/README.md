# Kite Connect Integration Guide

This module integrates your trading algorithm with Zerodha's Kite Connect API.

## Setup Instructions

### 1. Register on Kite Developer Portal

1. Visit [Kite Developer Portal](https://developers.kite.trade/signup)
2. Sign up and create an account
3. Navigate to "My Apps" and click "Create New App"

### 2. Configure Redirect URL and Postback URL

When creating your app, you'll need to specify:

#### **Redirect URL** (Required)
This is where users are redirected after OAuth authentication.

**For Local Testing:**
```
http://127.0.0.1:8000
```
or
```
http://localhost:8000
```

**For Production:**
```
https://yourdomain.com/callback
```
(Must be HTTPS in production)

#### **Postback URL** (Optional)
This receives real-time order update notifications. Leave empty if not using.

**Example:**
```
https://yourdomain.com/postback
```

### 3. Get API Credentials

After creating your app, you'll receive:
- **API Key**: Your application's API key
- **API Secret**: Your application's secret key

### 4. Configure Your Application

1. Copy `kite_config_example.py` to `kite_config.py`:
   ```bash
   cp kite_integration/kite_config_example.py kite_integration/kite_config.py
   ```

2. Edit `kite_config.py` and fill in your credentials:
   ```python
   API_KEY = "your_api_key_here"
   API_SECRET = "your_api_secret_here"
   REDIRECT_URL = "http://127.0.0.1:8000"  # Must match Kite Developer Portal
   ```

3. **Important**: Add `kite_config.py` to `.gitignore` to keep credentials secure!

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

```python
from kite_integration.kite_auth_helper import quick_authenticate
from kite_integration.kite_data_fetcher import KiteDataFetcher
from main_algorithm import StockAnalyzer

# Authenticate (will open browser for first-time login)
kite = quick_authenticate("kite_integration/kite_config.py")

# Fetch and analyze data
fetcher = KiteDataFetcher(kite)
result = fetcher.fetch_and_analyze("NSE", "RELIANCE", days=100)

# Get trading signals
signals = result['signals']
for signal in signals:
    print(f"Case {signal['case']}: Entry={signal['entry_price']:.2f}")
```

### Manual Authentication

```python
from kite_integration.kite_auth_helper import authenticate_kite

kite = authenticate_kite(
    api_key="your_api_key",
    api_secret="your_api_secret",
    redirect_url="http://127.0.0.1:8000"
)
```

### Fetch OHLC Data

```python
from datetime import datetime, timedelta
from kite_integration.kite_connector import KiteConnector

kite = KiteConnector(api_key, api_secret, redirect_url)
kite.set_access_token(access_token)

# Get instrument token
token = kite.get_instrument_token("NSE", "RELIANCE")

# Fetch data
ohlc_data = kite.get_ohlc_data(
    instrument_token=token,
    from_date=datetime.now() - timedelta(days=100),
    to_date=datetime.now(),
    interval="day"
)
```

### Place Orders

```python
# Place a market order
order = kite.place_order(
    variety="regular",
    exchange="NSE",
    tradingsymbol="RELIANCE",
    transaction_type="SELL",
    quantity=1,
    order_type="MARKET",
    product="MIS"  # Intraday
)
```

## Important Notes

### Redirect URL Requirements

1. **Must match exactly**: The redirect URL in your code must match exactly with the one registered in Kite Developer Portal
2. **HTTPS for production**: Use HTTPS URLs in production environments
3. **Local testing**: `http://127.0.0.1:8000` or `http://localhost:8000` work for local development

### Postback URL (Optional)

- Only needed if you want real-time order update notifications
- Must be a publicly accessible HTTPS endpoint
- Your server must handle POST requests with order update data

### Access Token

- Access tokens are valid for the trading day
- The module automatically saves tokens for reuse
- Saved in `kite_access_token.txt` by default
- Add this file to `.gitignore` for security

## Security Best Practices

1. **Never commit credentials**: Add `kite_config.py` and `kite_access_token.txt` to `.gitignore`
2. **Use environment variables**: For production, consider using environment variables instead of config files
3. **HTTPS only**: Always use HTTPS URLs in production
4. **Token storage**: Store access tokens securely and never share them

## Troubleshooting

### "Invalid redirect URL" error
- Ensure the redirect URL in your code matches exactly with Kite Developer Portal
- Check for trailing slashes or protocol differences (http vs https)

### "Invalid request token" error
- Request tokens are single-use and expire quickly
- Make sure you're using a fresh token from the redirect URL

### "Access token expired" error
- Access tokens expire at end of trading day
- Re-authenticate to get a new token

## Example: Complete Workflow

```python
from kite_integration.kite_auth_helper import quick_authenticate
from kite_integration.kite_data_fetcher import KiteDataFetcher

# 1. Authenticate
kite = quick_authenticate()

# 2. Fetch and analyze
fetcher = KiteDataFetcher(kite)
result = fetcher.fetch_and_analyze("NSE", "RELIANCE", days=100)

# 3. Get signals
signals = result['signals']

# 4. Execute trades based on signals
for signal in signals:
    if signal['case'] == '1a':  # Example: only trade Case 1.a signals
        # Place order logic here
        print(f"Signal detected: {signal}")
```

## Support

For Kite Connect API documentation, visit:
- [Kite Connect Docs](https://kite.trade/docs/connect/v3/)
- [Kite Developer Portal](https://developers.kite.trade/)

