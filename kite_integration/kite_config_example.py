"""
Kite Connect Configuration Example
Copy this file to kite_config.py and fill in your credentials
DO NOT commit kite_config.py to version control
"""

# Kite Connect API Credentials
# Get these from https://developers.kite.trade/apps
API_KEY = "your_api_key_here"
API_SECRET = "your_api_secret_here"

# Redirect URL - Must match the URL registered in Kite Developer Portal
# For local testing:
REDIRECT_URL = "http://127.0.0.1:8000"

# For production (use HTTPS):
# REDIRECT_URL = "https://yourdomain.com/callback"

# Postback URL (Optional) - For receiving order update notifications
# Leave empty if not using postback
POSTBACK_URL = ""  # e.g., "https://yourdomain.com/postback"

# Access Token Storage
# Set to True to save access token for future use
SAVE_ACCESS_TOKEN = True
ACCESS_TOKEN_FILE = "kite_access_token.txt"

