import functions_framework
from flask import jsonify
import requests
from datetime import datetime, timedelta
import time

def get_yahoo_auth_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

@functions_framework.http
def get_stock_price(request):
    """
    HTTP Cloud Function to get stock prices using Yahoo Finance API directly.
    Args:
        request (flask.Request): The request object
        It should contain a 'ticker' parameter
    Returns:
        The stock data response
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        # Get the ticker from the request
        request_json = request.get_json(silent=True)
        request_args = request.args

        if request_json and 'ticker' in request_json:
            ticker = request_json['ticker']
        elif request_args and 'ticker' in request_args:
            ticker = request_args['ticker']
        else:
            return (jsonify({'error': 'No ticker provided'}), 400, headers)

        # Yahoo Finance API endpoints
        quote_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        
        # Get current timestamp and 7 days ago timestamp
        end = int(time.time())
        start = end - (7 * 24 * 60 * 60)  # 7 days ago
        
        # Parameters for the API request
        params = {
            'period1': start,
            'period2': end,
            'interval': '1d'
        }

        # Make the API request
        response = requests.get(
            quote_url,
            params=params,
            headers=get_yahoo_auth_headers()
        )
        
        if response.status_code != 200:
            return (jsonify({'error': 'Failed to fetch stock data'}), 500, headers)

        data = response.json()
        
        if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
            return (jsonify({'error': 'Invalid data received from Yahoo Finance'}), 500, headers)

        result = data['chart']['result'][0]
        quote = result['indicators']['quote'][0]
        
        # Get the most recent values
        current_price = quote['close'][-1]
        
        response_data = {
            'symbol': ticker,
            'currentPrice': current_price,
            'timestamp': result['timestamp'][-1],
            'historical': {
                'timestamps': result['timestamp'],
                'open': quote['open'],
                'high': quote['high'],
                'low': quote['low'],
                'close': quote['close'],
                'volume': quote['volume']
            }
        }

        return (jsonify(response_data), 200, headers)

    except Exception as e:
        return (jsonify({'error': str(e)}), 500, headers)
