from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.helpers import json_response
from utils.db import get_conn
import base64
import os
from datetime import datetime

pest_bp = Blueprint('pest', __name__)

# Sample pest detection responses (in real implementation, this would come from ML model)
MOCK_PESTS = {
    'aphids': {
        'name': 'Aphids',
        'confidence': 85,
        'recommendations': [
            'Use neem oil spray',
            'Introduce ladybugs as natural predators',
            'Remove affected leaves',
            'Apply insecticidal soap'
        ]
    },
    'spider_mites': {
        'name': 'Spider Mites',
        'confidence': 78,
        'recommendations': [
            'Increase humidity around plants',
            'Use miticide if infestation is severe',
            'Regularly spray leaves with water',
            'Isolate affected plants'
        ]
    },
    'no_pest': {
        'name': 'No Pest Detected',
        'confidence': 90,
        'recommendations': [
            'Continue regular monitoring',
            'Maintain good garden hygiene',
            'Practice crop rotation'
        ]
    }
}

@pest_bp.route('/pest/detect', methods=['POST'])
@jwt_required()
def pest_detect():
    user_id = get_jwt_identity().get('id')
    payload = request.get_json() or {}
    
    if 'image' not in payload:
        return json_response('error', 'No image provided', {}, 400)
        
    try:
        # Decode base64 image
        image_data = base64.b64decode(payload['image'])
        
        # In production: Save image to a proper storage service
        # For demo: Save to uploads folder with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        image_path = os.path.join(upload_dir, f'pest_{user_id}_{timestamp}.png')
        with open(image_path, 'wb') as f:
            f.write(image_data)
            
        # In production: Call ML model for detection
        # For demo: Return random mock result
        import random
        pest_type = random.choice(['aphids', 'spider_mites', 'no_pest'])
        pest_info = MOCK_PESTS[pest_type]
        
        # Save detection result to database
        conn = get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pest_detections 
                (user_id, image_path, pest_name, confidence_score, recommendations)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                user_id,
                os.path.basename(image_path),
                pest_info['name'],
                pest_info['confidence'],
                '\n'.join(pest_info['recommendations'])
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
            
        return json_response(
            'success',
            f"Detected {pest_info['name']} with {pest_info['confidence']}% confidence",
            {'pest': pest_info}
        )
        
    except Exception as e:
        current_app.logger.exception('Pest detection error')
        return json_response('error', 'Failed to process image', {'error': str(e)}, 500)

