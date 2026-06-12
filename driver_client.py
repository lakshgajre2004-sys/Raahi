from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'
CLIENT_TYPE = 'DRIVER'

@app.route('/')
def home():
    """Driver client dashboard"""
    return render_template_string(DRIVER_DASHBOARD_HTML)

@app.route('/api/driver/health', methods=['GET'])
def driver_health():
    """Health check for driver client"""
    try:
        server_response = requests.get(f'{SERVER_URL}/api/health', timeout=5)
        server_status = "Connected" if server_response.status_code == 200 else "Error"
    except:
        server_status = "Disconnected"
    
    return jsonify({
        'service': 'Driver Client API',
        'status': 'running',
        'server_connection': server_status,
        'client_type': CLIENT_TYPE,
        'timestamp': datetime.now().isoformat(),
        'port': 6000
    })

@app.route('/api/driver/rides/available', methods=['GET'])
def get_available_rides():
    """Get rides available for drivers to accept"""
    try:
        print('🔍 Driver Client: Fetching available rides...')
        
        server_response = requests.get(
            f'{SERVER_URL}/api/drivers/rides/available',
            timeout=10
        )
        
        if server_response.status_code == 200:
            result = server_response.json()
            rides = result['data']
            
            # Add driver-specific information
            for ride in rides:
                ride['estimated_earnings'] = calculate_earnings(ride)
                ride['distance_info'] = f"~{get_estimated_distance(ride)} km"
                ride['priority'] = get_ride_priority(ride)
            
            # Sort by priority (most recent first, then by ride type)
            rides.sort(key=lambda x: (x['priority'], x['created_at']), reverse=True)
            
            return jsonify({
                'success': True,
                'message': f'Found {len(rides)} available rides',
                'available_rides': len(rides),
                'rides': rides,
                'client_type': 'driver'
            })
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to fetch available rides',
                'details': error_data.get('error', 'Unknown error')
            }), server_response.status_code
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Cannot connect to ride service'
        }), 503
        
    except Exception as e:
        return jsonify({
            'error': 'Driver client error',
            'details': str(e)
        }), 500

@app.route('/api/driver/rides/<int:ride_id>/accept', methods=['POST'])
def accept_ride(ride_id):
    """Accept a ride request"""
    data = request.get_json()
    driver_id = data.get('driver_id') if data else None
    
    if not driver_id:
        return jsonify({'error': 'driver_id is required'}), 400
    
    try:
        print(f'✅ Driver {driver_id} attempting to accept ride #{ride_id}')
        
        server_response = requests.put(
            f'{SERVER_URL}/api/drivers/rides/{ride_id}/accept',
            json={'driver_id': driver_id},
            timeout=10
        )
        
        if server_response.status_code == 200:
            result = server_response.json()
            return jsonify({
                'success': True,
                'message': 'Ride accepted! Navigate to pickup location.',
                'ride_info': result['data'],
                'next_action': 'start_trip',
                'estimated_arrival': '3-5 minutes'
            })
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to accept ride',
                'details': error_data.get('error', 'Unknown error')
            }), server_response.status_code
            
    except Exception as e:
        return jsonify({
            'error': 'Accept ride failed',
            'details': str(e)
        }), 500

@app.route('/api/driver/<int:driver_id>/rides', methods=['GET'])
def get_my_rides(driver_id):
    """Get rides assigned to this driver"""
    try:
        print(f'📋 Driver Client: Fetching rides for driver {driver_id}')
        
        server_response = requests.get(
            f'{SERVER_URL}/api/drivers/{driver_id}/rides',
            timeout=10
        )
        
        if server_response.status_code == 200:
            result = server_response.json()
            rides = result['data']
            
            # Add driver-specific information
            for ride in rides:
                ride['earnings'] = calculate_earnings(ride)
                ride['can_start'] = ride['status'] == 'accepted'
                ride['can_complete'] = ride['status'] == 'in_progress'
                ride['driver_status'] = get_driver_friendly_status(ride['status'])
            
            return jsonify({
                'success': True,
                'message': f'Found {len(rides)} assigned rides',
                'driver_id': driver_id,
                'rides': rides,
                'total_earnings': sum(ride['earnings'] for ride in rides if ride['status'] == 'completed')
            })
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to fetch driver rides',
                'details': error_data.get('error', 'Unknown error')
            }), server_response.status_code
            
    except Exception as e:
        return jsonify({
            'error': 'Driver client error',
            'details': str(e)
        }), 500

@app.route('/api/driver/rides/<int:ride_id>/update-status', methods=['PUT'])
def update_ride_status(ride_id):
    """Update ride status (start trip, complete trip)"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    driver_id = data.get('driver_id')
    new_status = data.get('status')
    
    if not driver_id or not new_status:
        return jsonify({'error': 'driver_id and status are required'}), 400
    
    try:
        print(f'🔄 Driver {driver_id} updating ride #{ride_id} to: {new_status}')
        
        server_response = requests.put(
            f'{SERVER_URL}/api/drivers/rides/{ride_id}/status',
            json={'driver_id': driver_id, 'status': new_status},
            timeout=10
        )
        
        if server_response.status_code == 200:
            result = server_response.json()
            
            # Return appropriate message based on status
            messages = {
                'in_progress': 'Trip started! Drive safely to destination.',
                'completed': 'Trip completed! Payment processed.',
                'cancelled': 'Ride cancelled. You can accept new rides.'
            }
            
            return jsonify({
                'success': True,
                'message': messages.get(new_status, f'Status updated to {new_status}'),
                'ride_info': result['data'],
                'new_status': new_status
            })
        else:
            error_data = server_response.json()
            return jsonify({
                'error': 'Failed to update ride status',
                'details': error_data.get('error', 'Unknown error')
            }), server_response.status_code
            
    except Exception as e:
        return jsonify({
            'error': 'Status update failed',
            'details': str(e)
        }), 500

# Helper functions
def calculate_earnings(ride):
    """Calculate estimated earnings for a ride"""
    base_rates = {
        'standard': 2.5,
        'premium': 3.5,
        'shared': 1.8
    }
    
    base_rate = base_rates.get(ride.get('ride_type', 'standard'), 2.5)
    estimated_distance = get_estimated_distance(ride)
    return round(base_rate * estimated_distance + 3.0, 2)  # Base fare + distance

def get_estimated_distance(ride):
    """Estimate distance based on locations (simplified)"""
    # In real app, you'd use Google Maps API or similar
    location_pairs = {
        ('Airport Terminal 1', 'Downtown Hotel'): 12.5,
        ('Home', 'Office Complex'): 8.2,
        ('Shopping Mall', 'Restaurant District'): 5.4,
        ('Train Station', 'Business Park'): 9.8
    }
    
    key = (ride.get('source_location'), ride.get('dest_location'))
    return location_pairs.get(key, 7.5)  # Default 7.5 km

def get_ride_priority(ride):
    """Calculate ride priority for sorting"""
    priority_map = {
        'premium': 3,
        'standard': 2,
        'shared': 1
    }
    return priority_map.get(ride.get('ride_type', 'standard'), 2)

def get_driver_friendly_status(status):
    """Convert status to driver-friendly message"""
    status_map = {
        'accepted': 'Navigate to pickup',
        'in_progress': 'Trip in progress',
        'completed': 'Trip completed',
        'cancelled': 'Cancelled'
    }
    return status_map.get(status, status)

# Driver Dashboard HTML
DRIVER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mini Uber - Driver Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
        }
        .header { text-align: center; color: white; margin-bottom: 20px; }
        .header h1 { font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .btn { 
            background: #28a745; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: all 0.2s;
        }
        .btn:hover { background: #218838; transform: translateY(-1px); }
        .btn-accept { background: #28a745; }
        .btn-start { background: #17a2b8; }
        .btn-complete { background: #fd7e14; }
        .btn-danger { background: #dc3545; }
        
        input, select { 
            width: 100%; 
            padding: 10px; 
            margin: 8px 0; 
            border: 2px solid #ddd; 
            border-radius: 6px; 
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        
        .status { padding: 10px; margin: 10px 0; border-radius: 6px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        
        .ride-item { 
            border: 1px solid #e0e0e0; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            background: #f9f9f9;
            transition: all 0.2s;
        }
        .ride-item:hover { 
            background: #f0f0f0; 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .ride-header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 10px; 
        }
        .ride-route { font-weight: bold; color: #333; font-size: 16px; }
        .ride-meta { font-size: 14px; color: #666; margin: 5px 0; }
        
        .status-badge { 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: bold; 
            text-transform: uppercase; 
        }
        .status-requested { background: #fff3cd; color: #856404; }
        .status-accepted { background: #d4edda; color: #155724; }
        .status-in_progress { background: #d1ecf1; color: #0c5460; }
        .status-completed { background: #e2e3e5; color: #383d41; }
        .status-cancelled { background: #f8d7da; color: #721c24; }
        
        .dashboard-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
        }
        
        @media (max-width: 768px) {
            .dashboard-grid { grid-template-columns: 1fr; }
        }
        
        .loading { text-align: center; padding: 20px; color: #666; }
        .earnings { font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Driver Dashboard</h1>
            <p>Accept rides and manage your trips</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>🔍 Available Rides</h2>
                <button onclick="loadAvailableRides()" class="btn">Refresh Available Rides</button>
                <div id="availableRidesResult">
                    <div class="loading">Click "Refresh Available Rides" to see available trips</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📋 My Rides</h2>
                <input type="number" id="driverIdFilter" placeholder="Enter Driver ID" value="456">
                <button onclick="loadMyRides()" class="btn">Load My Rides</button>
                <div id="myRidesResult">
                    <div class="loading">Enter your Driver ID and click "Load My Rides"</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function loadAvailableRides() {
            const resultDiv = document.getElementById('availableRidesResult');
            resultDiv.innerHTML = '<div class="loading">Loading available rides...</div>';
            
            try {
                const response = await fetch('/api/driver/rides/available');
                const result = await response.json();
                
                if (response.ok) {
                    if (result.rides.length === 0) {
                        resultDiv.innerHTML = '<div class="info">No rides available at the moment.</div>';
                        return;
                    }
                    
                    let html = `<h3>Available Rides (${result.rides.length} found)</h3>`;
                    result.rides.forEach(ride => {
                        html += `
                            <div class="ride-item">
                                <div class="ride-header">
                                    <div class="ride-route">🚗 ${ride.source_location} → ${ride.dest_location}</div>
                                    <div class="status-badge status-${ride.status}">${ride.status}</div>
                                </div>
                                <div class="ride-meta">
                                    <strong>Ride #${ride.id}</strong> | User: ${ride.user_id} | 
                                    Type: ${ride.ride_type} | Distance: ${ride.distance_info}
                                </div>
                                <div class="ride-meta">
                                    <span class="earnings">Estimated Earnings: $${ride.estimated_earnings}</span> | 
                                    ${new Date(ride.created_at).toLocaleString()}
                                </div>
                                <button onclick="acceptRide(${ride.id})" class="btn btn-accept">
                                    Accept Ride ($${ride.estimated_earnings})
                                </button>
                            </div>
                        `;
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ ${result.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
            }
        }
        
        async function loadMyRides() {
            const driverId = document.getElementById('driverIdFilter').value;
            if (!driverId) {
                document.getElementById('myRidesResult').innerHTML = '<div class="error">Please enter Driver ID</div>';
                return;
            }
            
            const resultDiv = document.getElementById('myRidesResult');
            resultDiv.innerHTML = '<div class="loading">Loading your rides...</div>';
            
            try {
                const response = await fetch(`/api/driver/${driverId}/rides`);
                const result = await response.json();
                
                if (response.ok) {
                    if (result.rides.length === 0) {
                        resultDiv.innerHTML = '<div class="info">No rides assigned to you yet.</div>';
                        return;
                    }
                    
                    let html = `
                        <h3>My Rides (${result.rides.length} total)</h3>
                        <div class="info">Total Earnings: <span class="earnings">$${result.total_earnings}</span></div>
                    `;
                    
                    result.rides.forEach(ride => {
                        let actionButton = '';
                        if (ride.can_start) {
                            actionButton = `<button onclick="updateRideStatus(${ride.id}, 'in_progress')" class="btn btn-start">Start Trip</button>`;
                        } else if (ride.can_complete) {
                            actionButton = `<button onclick="updateRideStatus(${ride.id}, 'completed')" class="btn btn-complete">Complete Trip</button>`;
                        }
                        
                        html += `
                            <div class="ride-item">
                                <div class="ride-header">
                                    <div class="ride-route">🚗 ${ride.source_location} → ${ride.dest_location}</div>
                                    <div class="status-badge status-${ride.status}">${ride.status}</div>
                                </div>
                                <div class="ride-meta">
                                    <strong>Ride #${ride.id}</strong> | User: ${ride.user_id} | 
                                    Earnings: <span class="earnings">$${ride.earnings}</span>
                                </div>
                                <div class="ride-meta">
                                    Status: ${ride.driver_status} | ${new Date(ride.created_at).toLocaleString()}
                                </div>
                                ${actionButton}
                            </div>
                        `;
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ ${result.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Network Error: ${error.message}</div>`;
            }
        }
        
        async function acceptRide(rideId) {
            const driverId = prompt('Enter your Driver ID:', '456');
            if (!driverId) return;
            
            try {
                const response = await fetch(`/api/driver/rides/${rideId}/accept`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ driver_id: parseInt(driverId) })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`✅ ${result.message}`);
                    loadAvailableRides(); // Refresh available rides
                    loadMyRides(); // Refresh my rides
                } else {
                    alert(`❌ ${result.error}: ${result.details}`);
                }
            } catch (error) {
                alert(`❌ Network Error: ${error.message}`);
            }
        }
        
        async function updateRideStatus(rideId, newStatus) {
            const driverId = document.getElementById('driverIdFilter').value;
            if (!driverId) {
                alert('Please enter your Driver ID first');
                return;
            }
            
            try {
                const response = await fetch(`/api/driver/rides/${rideId}/update-status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        driver_id: parseInt(driverId), 
                        status: newStatus 
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(`✅ ${result.message}`);
                    loadMyRides(); // Refresh my rides
                } else {
                    alert(`❌ ${result.error}: ${result.details}`);
                }
            } catch (error) {
                alert(`❌ Network Error: ${error.message}`);
            }
        }
        
        // Auto-refresh available rides every 30 seconds
        setInterval(loadAvailableRides, 30000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print('🚕 Mini Uber Driver Client starting...')
    print('🌐 Driver dashboard: http://localhost:6000')
    print('📡 API endpoints: http://localhost:6000/api/driver/*')
    print(f'🔗 Connecting to server: {SERVER_URL}')
    # Added use_reloader=False to prevent the infinite restart loop
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)