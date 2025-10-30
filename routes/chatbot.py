from flask import Blueprint, request, current_app
from utils.helpers import json_response, validate_required_fields

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    payload = request.get_json() or {}
    missing = validate_required_fields(payload, ['message'])
    if missing:
        return json_response('error', f'Missing fields: {missing}', {}, 400)

    message = payload['message']
    # Placeholder: Echo-style AI response
    reply = f"You said: {message}. (This is a placeholder response from the chatbot.)"
    return json_response('success', 'Reply generated', {'reply': reply})
