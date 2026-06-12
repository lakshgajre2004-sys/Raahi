from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'

@app.route('/api/client/health', methods=['GET'])
def client_health():
    return jsonify({
        'status': 'Python Client API is running',
        'server_url': SERVER_URL,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/client/ride-request', methods=['POST'])
def submit_ride_request():
    # Get JSON data from request
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract required parameters
    source_location = data.get('source_location')
    dest_location = data.get('dest_location')
    user_id = data.get('user_id')
    
    # Validate required parameters
    if not source_location or not dest_location or not user_id:
        return jsonify({
            'error': 'Missing required parameters: source_location, dest_location, user_id'
        }), 400
    
    try:
        print('🔄 Client API: Processing ride request...')
        print(f'📍 Source: {source_location}')
        print(f'📍 Destination: {dest_location}')
        print(f'👤 User ID: {user_id}')
        
        # Forward request to server
        server_response = requests.post(f'{SERVER_URL}/api/rides', json={
            'source_location': source_location,
            'dest_location': dest_location,
            'user_id': user_id
        })
        
        print('✅ Client API: Request forwarded to server successfully')
        
        return jsonify({
            'success': True,
            'message': 'Ride request submitted via Python Client API',
            'client_timestamp': datetime.now().isoformat(),
            'server_response': server_response.json()
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Unable to connect to server',
            'server_url': SERVER_URL
        }), 503
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Client API internal error',
            'details': str(e)
        }), 500

@app.route('/api/client/rides/<int:user_id>', methods=['GET'])
def get_user_rides(user_id):
    try:
        print(f'🔍 Client API: Fetching rides for user {user_id}')
        
        server_response = requests.get(f'{SERVER_URL}/api/rides/user/{user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Ride history fetched via Python Client API',
            'user_id': user_id,
            'rides': server_response.json()['data']
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Unable to connect to server',
            'server_url': SERVER_URL
        }), 503
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Client API internal error',
            'details': str(e)
        }), 500

@app.route('/api/client/rides', methods=['GET'])
def get_all_rides():
    try:
        print('🔍 Client API: Fetching all rides')
        
        server_response = requests.get(f'{SERVER_URL}/api/rides')
        
        return jsonify({
            'success': True,
            'message': 'All rides fetched via Python Client API',
            'rides': server_response.json()['data']
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Unable to connect to server',
            'server_url': SERVER_URL
        }), 503
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Client API internal error', 
            'details': str(e)
        }), 500

if __name__ == '__main__':
    print('🚕 Mini Uber Python Client API starting...')
    print('📡 Client API endpoints:')
    print('   - POST http://localhost:4000/api/client/ride-request')
    print('   - GET  http://localhost:4000/api/client/rides/<user_id>')
    print('   - GET  http://localhost:4000/api/client/rides')
    print(f'🔗 Connects to server at: {SERVER_URL}')
    
    app.run(host='0.0.0.0', port=4000, debug=True)