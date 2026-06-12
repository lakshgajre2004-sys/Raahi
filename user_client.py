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

# --- All the Python functions for API endpoints are correct and do not need changes ---

@app.route('/api/user/health', methods=['GET'])
def user_health():
    """Health check for user client"""
    try:
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
    
    required_fields = ['user_id', 'source_location', 'dest_location']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        ride_data = {
            'user_id': data['user_id'],
            'source_location': data['source_location'],
            'dest_location': data['dest_location'],
            'ride_type': data.get('ride_type', 'standard'),
        }
        
        server_response = requests.post(f'{SERVER_URL}/api/users/rides', json=ride_data, timeout=10)
        
        if server_response.status_code == 201:
            result = server_response.json()
            return jsonify({
                'success': True,
                'message': 'Your ride has been requested successfully!',
                'ride_id': result['data']['id'],
                'data': result['data']
            }), 201
        else:
            return jsonify(server_response.json()), server_response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Cannot connect to ride service', 'details': str(e)}), 503

@app.route('/api/user/<int:user_id>/rides', methods=['GET'])
def get_my_rides(user_id):
    """Get ride history for a user"""
    try:
        server_response = requests.get(f'{SERVER_URL}/api/users/{user_id}/rides', timeout=10)
        
        if server_response.status_code == 200:
            result = server_response.json()
            rides = result.get('data', [])
            
            for ride in rides:
                ride['user_friendly_status'] = get_user_friendly_status(ride['status'])
                ride['can_cancel'] = ride['status'] in ['requested', 'accepted']
            
            return jsonify({
                'success': True,
                'rides': rides
            })
        else:
            return jsonify(server_response.json()), server_response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Cannot connect to ride service', 'details': str(e)}), 503

@app.route('/api/rides/<int:ride_id>/cancel', methods=['PUT'])
def cancel_ride_proxy(ride_id):
    """Proxy the cancel request to the main server"""
    data = request.get_json()
    try:
        server_response = requests.put(f'{SERVER_URL}/api/rides/{ride_id}/cancel', json=data, timeout=10)
        return server_response.json(), server_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Cannot connect to ride service', 'details': str(e)}), 503


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

USER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Dashboard - Mini Uber</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f2f5; }
        .container { max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        input, select, button { padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; width: 100%; box-sizing: border-box; }
        button { background-color: #007bff; color: white; cursor: pointer; border: none; font-size: 16px; }
        button:hover { opacity: 0.9; }
        .btn-danger { background-color: #dc3545; }
        #rideStatus, #ridesResult { margin-top: 20px; }
        .ride { border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px; background: #fafafa; }
        .status { padding: 10px; border-radius: 6px; text-align: center; }
        .status.success { background-color: #d4edda; color: #155724; }
        .status.error { background-color: #f8d7da; color: #721c24; }
        .fare { font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>👥 User Dashboard</h1>
        
        <h2>Request a New Ride</h2>
        <div id="rideForm">
            <input type="number" id="userId" placeholder="Your User ID (e.g., 123)" value="123">
            <input type="text" id="source" placeholder="Source Location" value="Home">
            <input type="text" id="destination" placeholder="Destination Location" value="Office Complex">
            <select id="rideType">
                <option value="standard">Standard</option>
                <option value="premium">Premium</option>
                <option value="shared">Shared</option>
            </select>
            <button onclick="requestRide()">Request Ride</button>
        </div>
        <div id="rideStatus"></div>
        
        <hr style="margin: 25px 0;">

        <h2>My Ride History</h2>
        <button onclick="loadMyRides()">Refresh Ride History</button>
        <div id="ridesResult"><div style="text-align: center; color: #666;">Click "Refresh" to see your rides</div></div>
    </div>

    <script>
        async function requestRide() {
            const userId = document.getElementById('userId').value;
            const source = document.getElementById('source').value;
            const destination = document.getElementById('destination').value;
            const rideType = document.getElementById('rideType').value;
            const statusDiv = document.getElementById('rideStatus');

            if (!userId || !source || !destination) {
                alert('Please fill in all fields.');
                return;
            }

            try {
                const response = await fetch('/api/user/request-ride', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: parseInt(userId),
                        source_location: source,
                        dest_location: destination,
                        ride_type: rideType
                    })
                });

                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `<div class="status success">✅ ${result.message} (Ride ID: ${result.ride_id})</div>`;
                    loadMyRides(); // Refresh history
                } else {
                    statusDiv.innerHTML = `<div class="status error">❌ ${result.error}: ${result.details || ''}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Network Error: ${error.message}</div>`;
            }
        }

        async function loadMyRides() {
            const userId = document.getElementById('userId').value;
            if (!userId) {
                alert('Please enter a User ID to see history.');
                return;
            }
            const resultDiv = document.getElementById('ridesResult');
            resultDiv.innerHTML = '<div style="text-align: center; color: #666;">Loading history...</div>';

            try {
                const response = await fetch(`/api/user/${userId}/rides`);
                const result = await response.json();
                
                if (response.ok && result.rides) {
                    if (result.rides.length === 0) {
                        resultDiv.innerHTML = '<div style="text-align: center; color: #666;">No rides found for this user.</div>';
                        return;
                    }
                    let html = `<h3>Your Rides (${result.rides.length} found)</h3>`;
                    result.rides.forEach(ride => {
                        // --- THIS IS THE FIX ---
                        const fare = ride.estimated_fare ? `<strong>Est. Fare: ₹${parseFloat(ride.estimated_fare).toFixed(2)}</strong>` : '';
                        const driver = ride.driver_id ? `| Driver #${ride.driver_id}` : '';
                        const cancelButton = ride.can_cancel ? `<button class="btn-danger" style="width: auto; padding: 8px 12px; font-size: 12px; margin-top: 10px;" onclick="cancelRide(${ride.id})">Cancel Ride</button>` : '';

                        html += `
                            <div class="ride">
                                <strong>Ride #${ride.id}</strong>: ${ride.source_location} → ${ride.dest_location}<br>
                                <small>Status: ${ride.user_friendly_status} ${driver} | ${new Date(ride.created_at).toLocaleString()}</small><br>
                                ${fare}
                                ${cancelButton}
                            </div>
                        `;
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="status error">❌ ${result.error || 'Failed to load rides.'}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="status error">❌ Network Error: ${error.message}</div>`;
            }
        }

        async function cancelRide(rideId) {
            const userId = document.getElementById('userId').value;
            if (!userId) {
                alert('User ID is required to cancel a ride.');
                return;
            }
            if (!confirm('Are you sure you want to cancel this ride?')) {
                return;
            }

            try {
                const response = await fetch(`/api/rides/${rideId}/cancel`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cancelled_by: 'user' })
                });

                const result = await response.json();
                
                if (response.ok) {
                    alert('✅ Ride cancelled successfully.');
                    loadMyRides();
                } else {
                    alert(`❌ Failed to cancel ride: ${result.details}`);
                }
            } catch (error) {
                alert(`❌ Network Error: ${error.message}`);
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
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    