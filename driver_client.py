from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import sys

app = Flask(__name__)
CORS(app)

SERVER_URL = 'http://localhost:3000'

DRIVER_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Driver Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .auth-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            max-width: 900px;
            width: 100%;
            display: flex;
            min-height: 500px;
        }
        .auth-sidebar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            flex: 1;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .auth-sidebar h1 { font-size: 32px; margin-bottom: 20px; }
        .auth-sidebar p { opacity: 0.9; line-height: 1.6; }
        .auth-content {
            flex: 1.5;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .auth-tabs {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            border-bottom: 2px solid #eee;
        }
        .auth-tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: #999;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .auth-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .auth-form { display: none; }
        .auth-form.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        
        /* Dashboard Styles */
        .dashboard-container {
            background: #f5f7fa;
            min-height: 100vh;
            padding: 20px;
        }
        .dashboard-header {
            background: white;
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .dashboard-header h2 { color: #667eea; margin: 0; }
        .status-toggle {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .switch {
            position: relative;
            width: 60px;
            height: 34px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider { background-color: #28a745; }
        input:checked + .slider:before { transform: translateX(26px); }
        .status-text {
            font-weight: 600;
            font-size: 18px;
        }
        .logout-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .panel {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .panel h3 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .ride-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .ride-card p { margin: 8px 0; }
        .ride-card .fare { color: #28a745; font-weight: bold; font-size: 18px; }
        .ride-btn {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 10px;
        }
        .accept-btn { background: #28a745; color: white; }
        .progress-btn { background: #17a2b8; color: white; }
        .complete-btn { background: #6c757d; color: white; }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-card .number { font-size: 32px; font-weight: bold; }
        .stat-card .label { opacity: 0.9; margin-top: 5px; }
        @media (max-width: 768px) {
            .auth-container { flex-direction: column; }
            .auth-sidebar { padding: 30px; }
        }
    </style>
</head>
<body>
    <!-- Authentication View -->
    <div id="auth-view" class="auth-container">
        <div class="auth-sidebar">
            <h1>Driver Portal</h1>
            <p>Join our platform and start earning by providing rides to passengers. Manage your rides, track earnings, and grow your business with us.</p>
        </div>
        <div class="auth-content">
            <div class="auth-tabs">
                <button class="auth-tab active" onclick="switchTab('login')">Login</button>
                <button class="auth-tab" onclick="switchTab('register')">Register</button>
            </div>
            
            <form id="login-form" class="auth-form active" onsubmit="login(event)">
                <div class="form-group">
                    <label>Driver ID</label>
                    <input type="number" id="loginDriverId" placeholder="Enter your driver ID" required>
                </div>
                <button type="submit" class="btn">Login to Dashboard</button>
            </form>
            
            <form id="register-form" class="auth-form" onsubmit="registerDriver(event)">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" id="regName" placeholder="Enter your full name" required>
                </div>
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" id="regEmail" placeholder="Enter your email" required>
                </div>
                <div class="form-group">
                    <label>Vehicle Details</label>
                    <input type="text" id="regVehicle" placeholder="e.g., Maruti Swift (DL-01-AB-1234)" required>
                </div>
                <button type="submit" class="btn">Create Account</button>
            </form>
        </div>
    </div>

    <!-- Dashboard View -->
    <div id="dashboard-view" class="dashboard-container" style="display: none;">
        <div class="dashboard-header">
            <h2 id="welcome-message">Welcome, Driver!</h2>
            <div style="display: flex; gap: 20px; align-items: center;">
                <div class="status-toggle">
                    <label class="switch">
                        <input type="checkbox" id="onlineToggle" onchange="toggleOnlineStatus()">
                        <span class="slider"></span>
                    </label>
                    <span id="statusText" class="status-text" style="color: #dc3545;">Offline</span>
                </div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="panel" id="current-ride-panel" style="display: none;">
                <h3>Current Ride</h3>
                <div id="current-ride-details"></div>
            </div>
            
            <div class="panel" id="available-rides-panel" style="display: none;">
                <h3>Available Rides</h3>
                <p style="background: #e7f3ff; padding: 10px; border-radius: 6px; font-size: 14px; margin-bottom: 15px;">
                    🔄 <strong>Auto-refreshing every 3 seconds</strong> - All drivers see the same queue
                </p>
                <button onclick="loadAvailableRides()" class="btn" style="margin-bottom: 15px;">Refresh Now</button>
                <div id="available-rides"></div>
            </div>
            
            <div class="panel" id="summary-panel" style="display: none; grid-column: 1 / -1;">
                <h3>Today's Summary</h3>
                <div id="ride-summary" class="summary-stats"></div>
                <div id="completed-rides-list"></div>
            </div>
        </div>
    </div>

    <script>
        let currentDriverId = null;
        let currentRideFare = 0;
        let queueRefreshInterval = null;

        function switchTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            
            if (tab === 'login') {
                document.querySelectorAll('.auth-tab')[0].classList.add('active');
                document.getElementById('login-form').classList.add('active');
            } else {
                document.querySelectorAll('.auth-tab')[1].classList.add('active');
                document.getElementById('register-form').classList.add('active');
            }
        }

        async function login(e) {
            e.preventDefault();
            const driverId = document.getElementById('loginDriverId').value;
            
            try {
                const response = await fetch(`/api/driver/${driverId}`);
                const result = await response.json();
                if (!result.success) throw new Error(result.error);
                
                currentDriverId = driverId;
                document.getElementById('auth-view').style.display = 'none';
                document.getElementById('dashboard-view').style.display = 'block';
                document.getElementById('welcome-message').textContent = `Welcome, ${result.data.name}!`;
                document.getElementById('onlineToggle').checked = false;
                document.getElementById('statusText').textContent = 'Offline';
                document.getElementById('statusText').style.color = '#dc3545';
            } catch (error) {
                alert(`Login Failed: ${error.message}`);
            }
        }

        function logout() {
            if (document.getElementById('onlineToggle').checked) {
                alert("Please go offline before logging out.");
                return;
            }
            stopQueueAutoRefresh(); // Stop auto-refresh on logout
            currentDriverId = null;
            document.getElementById('auth-view').style.display = 'flex';
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('loginDriverId').value = '';
        }

        async function registerDriver(e) {
            e.preventDefault();
            const name = document.getElementById('regName').value;
            const email = document.getElementById('regEmail').value;
            const vehicle = document.getElementById('regVehicle').value;
            
            try {
                const response = await fetch('/api/driver/register', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ name, email, vehicle_details: vehicle }) 
                });
                const result = await response.json();
                
                if (!response.ok) throw new Error(result.details || result.error || 'Registration failed');
                
                alert(`Registration successful! Your Driver ID is ${result.driver_id}`);
                switchTab('login');
                document.getElementById('loginDriverId').value = result.driver_id;
                document.getElementById('regName').value = '';
                document.getElementById('regEmail').value = '';
                document.getElementById('regVehicle').value = '';
            } catch (error) { 
                alert(`Registration Error: ${error.message}`); 
            }
        }

        async function toggleOnlineStatus() {
            const toggle = document.getElementById('onlineToggle');
            const newStatus = toggle.checked ? 'online' : 'offline';
            
            try {
                const response = await fetch(`/api/driver/${currentDriverId}/status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                
                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'Failed to update status');
                
                const statusText = document.getElementById('statusText');
                statusText.textContent = toggle.checked ? 'Online' : 'Offline';
                statusText.style.color = toggle.checked ? '#28a745' : '#dc3545';
                
                if (toggle.checked) {
                    checkActiveRide();
                    loadCompletedRides();
                    startQueueAutoRefresh(); // Auto-refresh queue
                } else {
                    stopQueueAutoRefresh(); // Stop auto-refresh
                    document.getElementById('current-ride-panel').style.display = 'none';
                    document.getElementById('available-rides-panel').style.display = 'none';
                    document.getElementById('summary-panel').style.display = 'none';
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
                toggle.checked = !toggle.checked;
            }
        }
        
        function startQueueAutoRefresh() {
            if (queueRefreshInterval) {
                clearInterval(queueRefreshInterval);
            }
            
            console.log('Starting auto-refresh for ride queue');
            loadAvailableRides(); // Load immediately
            
            queueRefreshInterval = setInterval(() => {
                console.log('Auto-refreshing queue...');
                loadAvailableRides();
            }, 1000); // Refresh every 1 second for near-instant updates
        }
        
        function stopQueueAutoRefresh() {
            if (queueRefreshInterval) {
                console.log('Stopping auto-refresh');
                clearInterval(queueRefreshInterval);
                queueRefreshInterval = null;
            }
        }

        async function checkActiveRide() {
            if (!currentDriverId) return;
            
            try {
                const response = await fetch(`/api/driver/${currentDriverId}/active-ride`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    displayCurrentRide(data.data);
                } else if (document.getElementById('onlineToggle').checked) {
                    loadAvailableRides();
                }
            } catch (error) {
                console.error('Error checking active ride:', error);
            }
        }

        function displayCurrentRide(ride) {
            document.getElementById('available-rides-panel').style.display = 'none';
            const panel = document.getElementById('current-ride-panel');
            currentRideFare = ride.fare;
            
            let actionButton = '';
            if (ride.status === 'accepted') {
                actionButton = `<button class="ride-btn progress-btn" onclick="updateRideStatus(${ride.id}, 'in_progress')">Start Ride</button>`;
            } else if (ride.status === 'in_progress') {
                actionButton = `<button class="ride-btn complete-btn" onclick="updateRideStatus(${ride.id}, 'completed')">Complete Ride</button>`;
            }
            
            document.getElementById('current-ride-details').innerHTML = `
                <div class="ride-card">
                    <p><strong>Status:</strong> ${ride.status.replace('_', ' ').toUpperCase()}</p>
                    <p><strong>From:</strong> ${ride.source_location}</p>
                    <p><strong>To:</strong> ${ride.dest_location}</p>
                    <p class="fare">Fare: ₹${ride.fare}</p>
                    ${actionButton}
                </div>
            `;
            panel.style.display = 'block';
        }

        async function updateRideStatus(rideId, newStatus) {
            try {
                const response = await fetch(`/api/driver/rides/${rideId}/update-status`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        driver_id: parseInt(currentDriverId), 
                        status: newStatus 
                    })
                });
                
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Failed to update status');
                
                if (newStatus === 'completed') {
                    alert(`Ride Completed! You earned ₹${currentRideFare}.`);
                    document.getElementById('current-ride-panel').style.display = 'none';
                    startQueueAutoRefresh(); // Resume auto-refresh after completing ride
                    loadCompletedRides();
                } else if (newStatus === 'accepted') {
                    stopQueueAutoRefresh(); // Stop auto-refresh when accepting a ride
                    checkActiveRide();
                } else {
                    alert(`Status updated to: ${newStatus.replace('_', ' ')}`);
                    checkActiveRide();
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }

        function acceptRide(rideId) {
            updateRideStatus(rideId, 'accepted');
        }

        async function loadAvailableRides() {
            if (!document.getElementById('onlineToggle').checked) return;
            
            document.getElementById('current-ride-panel').style.display = 'none';
            const panel = document.getElementById('available-rides-panel');
            panel.style.display = 'block';
            const ridesDiv = document.getElementById('available-rides');
            
            try {
                const response = await fetch('/api/driver/rides/available');
                const data = await response.json();
                
                if (!data.success || !data.data || data.data.length === 0) {
                    ridesDiv.innerHTML = '<p style="text-align: center; color: #999;">No available rides right now.</p>';
                    return;
                }
                
                // Show queue with positions
                ridesDiv.innerHTML = '<h4 style="color: #667eea; margin-bottom: 15px;">Ride Queue (First In, First Out)</h4>' +
                    data.data.map((ride, index) => `
                    <div class="ride-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                Queue #${index + 1}
                            </span>
                            <span style="color: #999; font-size: 12px;">Ride ID: ${ride.id}</span>
                        </div>
                        <p><strong>From:</strong> ${ride.source_location}</p>
                        <p><strong>To:</strong> ${ride.dest_location}</p>
                        <p class="fare">Fare: ₹${ride.fare}</p>
                        <p style="font-size: 12px; color: #666;">User ID: ${ride.user_id}</p>
                        <button class="ride-btn accept-btn" onclick="acceptRide(${ride.id})">Accept Ride</button>
                    </div>
                `).join('');
            } catch (error) {
                ridesDiv.innerHTML = '<p style="color: red;">Could not connect to server.</p>';
                console.error('Error loading available rides:', error);
            }
        }

        async function loadCompletedRides() {
            if (!currentDriverId) return;
            
            const summaryPanel = document.getElementById('summary-panel');
            summaryPanel.style.display = 'block';
            const summaryDiv = document.getElementById('ride-summary');
            
            try {
                const response = await fetch(`/api/driver/${currentDriverId}/completed-rides`);
                const data = await response.json();
                
                if (!data.success) throw new Error(data.details || data.error || 'Unknown server error');
                
                const summary = data.summary;
                summaryDiv.innerHTML = `
                    <div class="stat-card">
                        <div class="number">${summary.total_rides}</div>
                        <div class="label">Total Rides</div>
                    </div>
                    <div class="stat-card">
                        <div class="number">₹${summary.total_earnings.toFixed(2)}</div>
                        <div class="label">Total Earnings</div>
                    </div>
                `;
                
                const listDiv = document.getElementById('completed-rides-list');
                if (data.data.length === 0) {
                    listDiv.innerHTML = '<p style="text-align: center; color: #999;">No completed rides today.</p>';
                } else {
                    listDiv.innerHTML = '<h4 style="margin: 20px 0 15px 0;">Completed Today:</h4>' + data.data.map(ride => `
                        <div class="ride-card">
                            <p><strong>From:</strong> ${ride.source_location}</p>
                            <p><strong>To:</strong> ${ride.dest_location}</p>
                            <p class="fare">Earned: ₹${ride.fare}</p>
                        </div>
                    `).join('');
                }
            } catch (error) {
                summaryDiv.innerHTML = `<p style="color:red;">Could not load summary: ${error.message}</p>`;
                console.error('Error loading completed rides:', error);
            }
        }
    </script>
</body>
</html>
'''

# --- Python proxy endpoints (unchanged) ---
@app.route('/')
def home():
    return render_template_string(DRIVER_DASHBOARD_HTML)

@app.route('/api/driver/<int:driver_id>', methods=['GET'])
def proxy_get_driver_details(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (get driver): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/register', methods=['POST'])
def proxy_register_driver():
    try:
        res = requests.post(f'{SERVER_URL}/api/drivers/register', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (register): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/status', methods=['PUT'])
def proxy_update_driver_status(driver_id):
    try:
        res = requests.put(f'{SERVER_URL}/api/drivers/{driver_id}/status', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (update status): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/rides/available', methods=['GET'])
def proxy_get_available_rides():
    try:
        res = requests.get(f'{SERVER_URL}/api/rides/available')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (available rides): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/rides/<int:ride_id>/update-status', methods=['PUT'])
def proxy_update_ride_status(ride_id):
    try:
        res = requests.put(f'{SERVER_URL}/api/rides/{ride_id}/status', json=request.get_json())
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (update ride status): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/active-ride', methods=['GET'])
def proxy_get_active_ride(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}/active-ride')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (active ride): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

@app.route('/api/driver/<int:driver_id>/completed-rides', methods=['GET'])
def proxy_get_completed_rides(driver_id):
    try:
        res = requests.get(f'{SERVER_URL}/api/drivers/{driver_id}/completed-rides')
        return jsonify(res.json()), res.status_code
    except Exception as e:
        print(f"Proxy error (completed rides): {e}")
        return jsonify({'success': False, 'error': 'Server connection failed'}), 503

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f'Driver Portal running at http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)