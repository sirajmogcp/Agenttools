import functions_framework
import yfinance as yf
from flask import jsonify


@functions_framework.http

def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
 
    
    if request_json and 'ticker' in request_json:
        ticker = request_json['ticker']
    elif request_args and 'ticker' in request_args:
        ticker = request_args['ticker']
    else:
        ticker = 'GOOG'
    
    try:
       
        ticker_yahoo = yf.Ticker(ticker)
        data = ticker_yahoo.history()
        last_quote = data['Close'].iloc[-1]
    

        return jsonify({'ticker': ticker, 'price': last_quote})

    except Exception as e:
        return jsonify({'error': f'Failed to fetch stock data: {str(e)}'}), 500

