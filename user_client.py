from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'
CLIENT_TYPE = 'USER'

@app.route('/')
def home():
    """User client dashboard"""
    return render_template_string(USER_DASHBOARD_HTML)

@app.route('/api/user/health', methods=['GET'])
def user_health():
    """Health check for user client"""
    try:
        # Test server connection
        server_response = requests.get(f'{SERVER_URL}/api/health', timeout=5)
        server_status = "Connected" if server_response.status_code == 200 else "Error"
    except:
        server_status = "Disconnected"
    
    return jsonify({
        'service': 'User Client API',
        'status': 'running',
        'server_connection': server_status,
        'client_type': CLIENT_TYPE,
        'timestamp': datetime.now().isoformat(),
        'port': 5000
    })

@app.route('/api/user/request-ride', methods=['POST'])
def request_ride():
    """Request a new ride (User perspective)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No ride data provided'}), 400
    
    # Validate user data
    required_fields = ['user_id', 'source_location', 'dest_location']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        print(f'🚕 User Client: Processing ride request for user {data["user_id"]}')
        print(f'📍 Route: {data["source_location"]} → {data["dest_location"]}')
        
        # Add user client metadata
        ride_data = {
            'user_id': data['user_id'],
            'source_location': data['source_location'],
            'dest_location': data['dest_location'],
            'ride_type': data.get('ride_type', 'standard'),
            'client_type': 'user',
            'requested_via': 'user_client_api'
        }
        
        # Forward to server
        server_response = requests.post(
            f'{SERVER_URL}/api/users/rides',
            json=ride_data,
            timeout=10
        )
        
        if server_response.status_code == 201:
            result = server_response.json()
            print(f'✅ Ride request successful: #{result["data"]["id"]}')
            
            return jsonify({
                'success': True,
                'message': 'Your ride has been requested successfully!',
                'ride_id': result['data']['id'],
                'estimated_arrival': '5-10 minutes',
                'client_timestamp': datetime.now().isoformat(),
                'data': result['data']
            }), 201
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to request ride',
                'details': error_data.get('error', 'Unknown server error')
            }), server_response.status_code
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Cannot connect to ride service',
            'message': 'Please try again later or contact support'
        }), 503
        
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'message': 'The request took too long. Please try again.'
        }), 408
        
    except Exception as e:
        return jsonify({
            'error': 'User client error',
            'details': str(e)
        }), 500

@app.route('/api/user/<int:user_id>/rides', methods=['GET'])
def get_my_rides(user_id):
    """Get ride history for a user"""
    try:
        print(f'📋 User Client: Fetching rides for user {user_id}')
        
        server_response = requests.get(
            f'{SERVER_URL}/api/users/{user_id}/rides',
            timeout=10
        )
        
        if server_response.status_code == 200:
            result = server_response.json()
            rides = result['data']
            
            # Add user-friendly information
            for ride in rides:
                ride['user_friendly_status'] = get_user_friendly_status(ride['status'])
                ride['can_cancel'] = ride['status'] in ['requested', 'accepted']
            
            return jsonify({
                'success': True,
                'message': f'Found {len(rides)} rides',
                'user_id': user_id,
                'rides': rides,
                'client_type': 'user'
            })
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to fetch rides',
                'details': error_data.get('error', 'Unknown error')
            }), server_response.status_code
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Cannot connect to ride service'
        }), 503
        
    except Exception as e:
        return jsonify({
            'error': 'User client error',
            'details': str(e)
        }), 500

@app.route('/api/user/ride/<int:ride_id>/cancel', methods=['PUT'])
def cancel_ride(ride_id):
    """Cancel a ride (user perspective)"""
    data = request.get_json()
    user_id = data.get('user_id') if data else None
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        print(f'❌ User {user_id} requesting to cancel ride #{ride_id}')
        
        # Update ride status to cancelled
        server_response = requests.put(
            f'{SERVER_URL}/api/drivers/rides/{ride_id}/status',
            json={'status': 'cancelled', 'driver_id': 0, 'cancelled_by': 'user'},
            timeout=10
        )
        
        if server_response.status_code == 200:
            result = server_response.json()
            return jsonify({
                'success': True,
                'message': 'Your ride has been cancelled',
                'refund_status': 'processed',
                'data': result['data']
            })
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to cancel ride',
                'details': error_data.get('error', 'Unknown error')
            }), server_response.status_code
            
    except Exception as e:
        return jsonify({
            'error': 'Cancellation failed',
            'details': str(e)
        }), 500

def get_user_friendly_status(status):
    """Convert technical status to user-friendly message"""
    status_map = {
        'requested': 'Looking for a driver...',
        'accepted': 'Driver on the way!',
        'in_progress': 'In transit',
        'completed': 'Trip completed',
        'cancelled': 'Cancelled'
    }
    return status_map.get(status, status)

# Simple HTML dashboard for users
USER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mini Uber - User Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        input, select { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚕 Mini Uber - User Dashboard</h1>
            <p>Request rides and track your trips</p>
        </div>
        
        <div class="card">
            <h2>Request a Ride</h2>
            <form id="rideForm">
                <input type="number" id="userId" placeholder="Your User ID" value="123" required>
                <input type="text" id="sourceLocation" placeholder="Pickup Location" required>
                <input type="text" id="destLocation" placeholder="Destination" required>
                <select id="rideType">
                    <option value="standard">Standard Ride</option>
                    <option value="premium">Premium Ride</option>
                    <option value="shared">Shared Ride</option>
                </select>
                <button type="submit" class="btn">Request Ride</button>
            </form>
            <div id="requestResult"></div>
        </div>
        
        <div class="card">
            <h2>My Rides</h2>
            <input type="number" id="userIdFilter" placeholder="Enter User ID" value="123">
            <button onclick="loadMyRides()" class="btn">Load My Rides</button>
            <div id="ridesResult"></div>
        </div>
    </div>

    <script>
        document.getElementById('rideForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const rideData = {
                user_id: parseInt(document.getElementById('userId').value),
                source_location: document.getElementById('sourceLocation').value,
                dest_location: document.getElementById('destLocation').value,
                ride_type: document.getElementById('rideType').value
            };
            
            try {
                const response = await fetch('/api/user/request-ride', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(rideData)
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('requestResult');
                
                if (response.ok) {
                    resultDiv.innerHTML = `<div class="status success">✅ ${result.message} Ride ID: #${result.ride_id}</div>`;
                    document.getElementById('rideForm').reset();
                    document.getElementById('userId').value = '123';
                } else {
                    resultDiv.innerHTML = `<div class="status error">❌ ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('requestResult').innerHTML = `<div class="status error">❌ Network Error: ${error.message}</div>`;
            }
        });
        
        async function loadMyRides() {
            const userId = document.getElementById('userIdFilter').value;
            if (!userId) return;
            
            try {
                const response = await fetch(`/api/user/${userId}/rides`);
                const result = await response.json();
                const resultDiv = document.getElementById('ridesResult');
                
                if (response.ok) {
                    let html = `<h3>Your Rides (${result.rides.length} found)</h3>`;
                    result.rides.forEach(ride => {
                        html += `
                            <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 4px;">
                                <strong>Ride #${ride.id}</strong> - ${ride.source_location} → ${ride.dest_location}<br>
                                <small>Status: ${ride.user_friendly_status} | ${new Date(ride.created_at).toLocaleString()}</small>
                            </div>
                        `;
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="status error">❌ ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('ridesResult').innerHTML = `<div class="status error">❌ Network Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print('👥 Mini Uber User Client starting...')
    print('🌐 User dashboard: http://localhost:5000')
    print('📡 API endpoints: http://localhost:5000/api/user/*')
    print(f'🔗 Connecting to server: {SERVER_URL}')
    app.run(host='0.0.0.0', port=5000, debug=True)