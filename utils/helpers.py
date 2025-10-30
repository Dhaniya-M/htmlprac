from flask import jsonify

def json_response(status: str, message: str, data=None, code=200):
    if data is None:
        data = {}
    payload = {"status": status, "message": message, "data": data}
    return jsonify(payload), code

def validate_required_fields(payload: dict, fields: list):
    missing = [f for f in fields if f not in payload or payload.get(f) in (None, '')]
    return missing
