from flask import Flask, request, make_response, jsonify
import json
import functions_framework
import yfinance as yf

app = Flask(__name__)

@app.route('/get_stock_price', methods=['GET'])
def get_stock_price(request):
    
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

