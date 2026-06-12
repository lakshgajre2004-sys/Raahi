from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# In-memory storage for rides
rides = []
ride_id_counter = 1

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'Python Server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/rides', methods=['POST'])
def submit_ride_request():
    global ride_id_counter
    
    # Get JSON data from request
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract required fields
    source_location = data.get('source_location')
    dest_location = data.get('dest_location') 
    user_id = data.get('user_id')
    
    # Validate required fields
    if not source_location or not dest_location or not user_id:
        return jsonify({
            'error': 'Missing required fields: source_location, dest_location, user_id'
        }), 400
    
    # Create ride object
    new_ride = {
        'id': ride_id_counter,
        'user_id': int(user_id),
        'source_location': source_location,
        'dest_location': dest_location,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    ride_id_counter += 1
    
    # Add to in-memory storage
    rides.append(new_ride)
    
    # Print the required message and display data
    print('\n📝 We will store this data in Postgres now')
    print('==========================================')
    print('📊 Ride Request Data:')
    print(f'- Ride ID: {new_ride["id"]}')
    print(f'- User ID: {new_ride["user_id"]}')
    print(f'- Source Location: {new_ride["source_location"]}')
    print(f'- Destination Location: {new_ride["dest_location"]}')
    print(f'- Status: {new_ride["status"]}')
    print(f'- Timestamp: {new_ride["created_at"]}')
    print('==========================================\n')
    
    return jsonify({
        'success': True,
        'message': 'Ride request submitted successfully',
        'data': new_ride
    }), 201

@app.route('/api/rides', methods=['GET'])
def get_all_rides():
    return jsonify({
        'success': True,
        'data': rides
    })

@app.route('/api/rides/user/<int:user_id>', methods=['GET'])
def get_user_rides(user_id):
    user_rides = [ride for ride in rides if ride['user_id'] == user_id]
    return jsonify({
        'success': True,
        'data': user_rides
    })

if __name__ == '__main__':
    print('🚗 Mini Uber Python Server starting...')
    print('📡 API endpoints available at:')
    print('   - POST http://localhost:3000/api/rides (submit ride request)')
    print('   - GET  http://localhost:3000/api/rides (get all rides)')
    print('   - GET  http://localhost:3000/api/rides/user/<user_id> (get user rides)')
    
    app.run(host='0.0.0.0', port=3000, debug=True)