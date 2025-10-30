from flask import Blueprint, request
from utils.helpers import json_response, validate_required_fields

soil_bp = Blueprint('soil', __name__)


@soil_bp.route('/soil-test', methods=['POST'])
def soil_test():
    payload = request.get_json() or {}
    missing = validate_required_fields(payload, ['ph', 'nitrogen', 'phosphorus', 'potassium'])
    if missing:
        return json_response('error', f'Missing fields: {missing}', {}, 400)

    ph = float(payload['ph'])
    n = float(payload['nitrogen'])
    p = float(payload['phosphorus'])
    k = float(payload['potassium'])

    recommendations = []
    if ph < 5.5:
        recommendations.append('Soil is acidic: consider liming to increase pH')
    elif ph > 7.5:
        recommendations.append('Soil is alkaline: consider sulfur or organic matter to lower pH')
    else:
        recommendations.append('Soil pH is within optimal range')

    if n < 10:
        recommendations.append('Nitrogen is low: apply nitrogen-rich fertilizer')
    if p < 10:
        recommendations.append('Phosphorus is low: apply phosphorus fertilizer')
    if k < 100:
        recommendations.append('Potassium is low: apply potassium fertilizer')

    data = {
        'ph': ph,
        'n': n,
        'p': p,
        'k': k,
        'recommendations': recommendations
    }
    return json_response('success', 'Soil test processed', data)
