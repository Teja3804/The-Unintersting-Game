"""
Kite Connect Authentication Helper
Simplifies the OAuth authentication flow
"""

import webbrowser
from urllib.parse import urlparse, parse_qs
from .kite_connector import KiteConnector, save_access_token, load_access_token


def authenticate_kite(api_key: str, api_secret: str, redirect_url: str = "http://127.0.0.1:8000",
                      save_token: bool = True, token_file: str = "kite_access_token.txt") -> KiteConnector:
    """
    Complete authentication flow for Kite Connect
    
    This function:
    1. Checks for saved access token
    2. If not found, opens browser for login
    3. Prompts user to paste redirect URL with request token
    4. Generates session and saves token
    
    Args:
        api_key: Your Kite Connect API key
        api_secret: Your Kite Connect API secret
        redirect_url: Redirect URL registered in Kite Developer Portal
        save_token: Whether to save access token for future use
        token_file: File path to save/load access token
        
    Returns:
        Authenticated KiteConnector instance
    """
    connector = KiteConnector(api_key, api_secret, redirect_url)
    
    # Try to load saved access token
    saved_token = load_access_token(token_file)
    if saved_token:
        try:
            connector.set_access_token(saved_token)
            print("✓ Successfully loaded saved access token")
            return connector
        except Exception as e:
            print(f"⚠ Saved token invalid: {str(e)}")
            print("Proceeding with new authentication...")
    
    # Generate login URL
    login_url = connector.get_login_url()
    print("\n" + "="*60)
    print("KITE CONNECT AUTHENTICATION")
    print("="*60)
    print(f"\n1. Opening browser for login...")
    print(f"   Login URL: {login_url}")
    
    # Open browser
    webbrowser.open(login_url)
    
    print(f"\n2. After logging in, you'll be redirected to:")
    print(f"   {redirect_url}?request_token=XXXXX&action=login&status=success")
    print(f"\n3. Copy the ENTIRE redirect URL from your browser")
    print(f"   (or just the request_token value)")
    
    # Get request token from user
    redirect_url_with_token = input("\nPaste the redirect URL or request_token: ").strip()
    
    # Extract request token
    if redirect_url_with_token.startswith("http"):
        # Parse URL to get request_token
        parsed = urlparse(redirect_url_with_token)
        params = parse_qs(parsed.query)
        request_token = params.get('request_token', [None])[0]
    else:
        # Assume user pasted just the token
        request_token = redirect_url_with_token
    
    if not request_token:
        raise ValueError("Invalid request token. Please provide a valid redirect URL or token.")
    
    # Generate session
    print("\n4. Generating session...")
    try:
        session_data = connector.generate_session(request_token)
        print("✓ Authentication successful!")
        print(f"  User ID: {session_data.get('user_id', 'N/A')}")
        
        # Save token if requested
        if save_token:
            save_access_token(connector.access_token, token_file)
            print(f"✓ Access token saved to {token_file}")
        
        return connector
        
    except Exception as e:
        raise Exception(f"Authentication failed: {str(e)}")


def quick_authenticate(config_file: str = "kite_config.py") -> KiteConnector:
    """
    Quick authentication using config file
    
    Args:
        config_file: Path to config file with API_KEY, API_SECRET, etc.
        
    Returns:
        Authenticated KiteConnector instance
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("kite_config", config_file)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        return authenticate_kite(
            api_key=config.API_KEY,
            api_secret=config.API_SECRET,
            redirect_url=getattr(config, 'REDIRECT_URL', 'http://127.0.0.1:8000'),
            save_token=getattr(config, 'SAVE_ACCESS_TOKEN', True),
            token_file=getattr(config, 'ACCESS_TOKEN_FILE', 'kite_access_token.txt')
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file '{config_file}' not found. "
            f"Please create it using kite_config_example.py as a template."
        )
    except Exception as e:
        raise Exception(f"Failed to load config: {str(e)}")

