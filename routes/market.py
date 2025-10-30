from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required
from utils.helpers import json_response
from utils.db import get_conn

market_bp = Blueprint('market', __name__)

# Mock data for development
MOCK_DATA = {
    'TN': {
        'rice': [
            {'market': 'Chennai', 'variety': 'Common', 'min_price': 2000, 'max_price': 2500, 'modal_price': 2250},
            {'market': 'Coimbatore', 'variety': 'Grade A', 'min_price': 2100, 'max_price': 2600, 'modal_price': 2400}
        ],
        'wheat': [
            {'market': 'Chennai', 'variety': 'Sharbati', 'min_price': 1800, 'max_price': 2200, 'modal_price': 2000},
            {'market': 'Coimbatore', 'variety': 'Lokwan', 'min_price': 1850, 'max_price': 2250, 'modal_price': 2100}
        ]
    },
    'KA': {
        'rice': [
            {'market': 'Bangalore', 'variety': 'Common', 'min_price': 2100, 'max_price': 2600, 'modal_price': 2350}
        ],
        'wheat': [
            {'market': 'Bangalore', 'variety': 'Lokwan', 'min_price': 1900, 'max_price': 2300, 'modal_price': 2100}
        ]
    }
}

@market_bp.route('/market/prices', methods=['GET'])
@jwt_required()
def get_prices():
    state = request.args.get('state', 'TN')
    crop = request.args.get('crop', 'rice')

    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Try to fetch from DB first
        cursor.execute('''
            SELECT market, variety, min_price, max_price, modal_price 
            FROM market_prices 
            WHERE state = %s AND crop_name = %s
            ORDER BY market
        ''', (state, crop))
        
        rows = cursor.fetchall()
        
        # If no data in DB, use mock data
        if not rows:
            state_data = MOCK_DATA.get(state, {})
            rows = state_data.get(crop, [])
            
        return json_response('success', 'Prices fetched successfully', {'prices': rows})

    except Exception as e:
        current_app.logger.exception('Error fetching market prices')
        # Fallback to mock data on error
        try:
            rows = MOCK_DATA[state][crop]
        except KeyError:
            rows = []
        return json_response('success', 'Prices fetched (mock)', {'prices': rows})
        
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
